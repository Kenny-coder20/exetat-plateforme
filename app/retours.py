"""Boucle d'amélioration : mémoire des corrections des validateurs et réinjection dans la génération.

Étage 1 — enregistrer() : à chaque décision d'un validateur, on conserve la décision, le motif, l'observation et,
          champ par champ, le texte AVANT et APRÈS correction.
Étage 2 — consignes_pour() : à chaque génération, on dérive de cette mémoire (30 derniers jours, même discipline)
          des consignes correctives, des exemples avant/après et des items de référence validés sans retouche.
          Les retours entrent dans la commande comme DONNÉES (statistiques et exemples), jamais comme instructions brutes.
Étage 3 — tableau() : indicateurs qualité pour la coordination.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from .db import one, rows

CHAMPS_LISIBLES = {
    "titre": "titre", "tige": "énoncé", "p1": "proposition 1", "p2": "proposition 2", "p3": "proposition 3",
    "p4": "proposition 4", "p5": "proposition 5", "reponse": "bonne réponse", "correction_detaillee": "correction détaillée",
    "erreurs_distracteurs": "erreurs des distracteurs", "chapitre": "chapitre", "difficulte": "difficulté",
    "texte": "texte de la situation", "document_texte": "document", "synthese": "synthèse",
}

# Traduction de chaque motif de rejet normalisé en consigne corrective pour le modèle.
CONSIGNES_PAR_MOTIF = {
    "Réponse marquée fausse": "vérifie la bonne réponse par un calcul ou un raisonnement complet avant d'écrire les propositions ; recalcule une seconde fois à partir des données de l'énoncé",
    "Plusieurs réponses possibles": "assure l'unicité : aucune autre proposition ne doit être défendable même avec une approximation ou une autre convention ; écarte les propositions numériquement trop proches",
    "Hors programme ou niveau inadapté": "reste strictement dans le chapitre indiqué et le niveau de 4e des humanités ; pas de notion d'université ni de méthode non enseignée",
    "Énoncé confus ou trop long": "énoncé de 35 à 75 mots, phrases courtes, une seule question, grandeur demandée nommée explicitement",
    "Données ou faits inexacts": "n'utilise que des données vérifiables et réalistes (ordres de grandeur, dates, noms, constantes) ; en cas de doute, choisis une donnée simple et sûre",
    "Contexte artificiel ou irréaliste": "le contexte doit fournir une donnée réellement utilisée dans la résolution ; supprime tout habillage décoratif ; situation plausible dans la vie congolaise",
    "Doublon d'une autre question": "varie le savoir essentiel, les données et l'angle de la question par rapport aux items déjà produits sur le chapitre",
}


# ------------------------------------------------------------------ étage 1 : mémoire

def enregistrer(con, *, item_id: str, type_: str, decision: str, validateur: str, motif: str | None, observations: str | None,
                meta: dict, diffs: list[tuple[str, str, str]]) -> None:
    """Conserve la décision et, s'il y a eu retouches, une ligne par champ modifié (avant / après)."""
    date = datetime.now().isoformat(timespec="minutes")
    base = (item_id, type_, meta.get("discipline"), meta.get("sous_discipline"), meta.get("epreuve_code"), meta.get("chapitre"),
            validateur, date, decision, motif, observations)
    sql = ("INSERT INTO corrections(item_id, type, discipline, sous_discipline, epreuve_code, chapitre, validateur, date, decision, "
           "motif, observations, champ, avant, apres) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
    if diffs:
        for champ, avant, apres in diffs:
            con.execute(sql, base + (champ, str(avant) if avant is not None else None, str(apres) if apres is not None else None))
    else:
        con.execute(sql, base + (None, None, None))


# ------------------------------------------------------------------ étage 2 : réinjection

def _depuis(jours: int) -> str:
    return (datetime.now() - timedelta(days=jours)).isoformat(timespec="minutes")


def _tronquer(s: str | None, n: int = 260) -> str:
    s = (s or "").strip().replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def consignes_pour(con, discipline: str, sous_discipline: str | None = None, epreuve_code: str | None = None,
                   jours: int = 30, max_exemples: int = 4, max_references: int = 2) -> str:
    """Bloc « RETOURS DES VALIDATEURS » à joindre à la commande ; chaîne vide si la mémoire est vide."""
    depuis = _depuis(jours)
    filtre, params = "discipline=? AND date>=?", [discipline, depuis]
    if sous_discipline:
        filtre += " AND (sous_discipline=? OR sous_discipline IS NULL)"
        params.append(sous_discipline)

    # décisions distinctes (une ligne par item et par décision, pas par champ)
    decisions = rows(con, f"SELECT item_id, decision, motif, MAX(date) d FROM corrections WHERE {filtre} AND type='item' "
                          f"GROUP BY item_id, decision, motif", params)
    if not decisions:
        return ""
    nb = len({d["item_id"] for d in decisions})
    rejets = [d for d in decisions if d["decision"] == "rejete"]
    bloc = [f"RETOURS DES VALIDATEURS EN {discipline.upper()} ({jours} derniers jours, {nb} question(s) relue(s), {len(rejets)} rejet(s))"]

    # 1. motifs de rejet fréquents -> consignes
    if rejets:
        comptes: dict[str, int] = {}
        for r in rejets:
            m = (r["motif"] or "Autre").split(" (")[0]
            comptes[m] = comptes.get(m, 0) + 1
        bloc.append("Motifs de rejet les plus fréquents et consignes qui en découlent :")
        for m, c in sorted(comptes.items(), key=lambda x: -x[1])[:4]:
            part = round(100 * c / len(rejets))
            consigne = CONSIGNES_PAR_MOTIF.get(m)
            bloc.append(f"- {m} : {c} rejet(s), {part} % → {consigne}" if consigne else f"- {m} : {c} rejet(s), {part} %")

    # 2. exemples avant / après (corrections réelles d'enseignants)
    ex = rows(con, f"SELECT champ, avant, apres, observations FROM corrections WHERE {filtre} AND type='item' AND champ IS NOT NULL "
                   f"AND champ IN ('tige','p1','p2','p3','p4','p5','correction_detaillee','reponse') ORDER BY date DESC LIMIT ?",
              params + [max_exemples * 3])
    vus, exemples = set(), []
    for e in ex:
        cle = (e["champ"], e["apres"])
        if cle in vus or (e["avant"] or "") == (e["apres"] or ""):
            continue
        vus.add(cle)
        exemples.append(e)
        if len(exemples) >= max_exemples:
            break
    if exemples:
        bloc.append("Exemples de corrections faites par des enseignants (à imiter, sans les recopier) :")
        for e in exemples:
            ligne = f"- {CHAMPS_LISIBLES.get(e['champ'], e['champ'])} — AVANT : « {_tronquer(e['avant'])} » → APRÈS : « {_tronquer(e['apres'])} »"
            if e["observations"]:
                ligne += f" (remarque : {_tronquer(e['observations'], 120)})"
            bloc.append(ligne)

    # 3. observations libres sur les rejets (données, pas instructions)
    obs = rows(con, f"SELECT DISTINCT observations FROM corrections WHERE {filtre} AND decision='rejete' AND observations IS NOT NULL "
                    f"AND observations<>'' ORDER BY observations LIMIT 4", params)
    if obs:
        bloc.append("Remarques d'enseignants sur des questions rejetées :")
        bloc += [f"- « {_tronquer(o['observations'], 160)} »" for o in obs]

    # 4. items validés sans retouche : référence de ce qui est attendu
    refs_sql = ("SELECT tige, p1, p2, p3, p4, p5, reponse FROM items WHERE discipline=? AND statut_validation='valide' "
                "AND version<>'corrigée' AND situation_id IS NULL")
    refs_params: list = [discipline]
    if sous_discipline:
        refs_sql += " AND sous_discipline=?"
        refs_params.append(sous_discipline)
    refs = rows(con, refs_sql + " ORDER BY date_validation DESC LIMIT ?", refs_params + [max_references])
    if refs:
        bloc.append("Questions validées telles quelles par les enseignants (niveau et forme attendus ; ne pas les reproduire) :")
        for r in refs:
            bloc.append(f"- « {_tronquer(r['tige'], 300)} » — réponse {r['reponse']} : « {_tronquer(r['p' + str(r['reponse'])], 100)} »")

    bloc.append("Ces retours sont des constats de terrain : tiens-en compte dans chaque item, sans les citer.")
    return "\n".join(bloc) + "\n"


# ------------------------------------------------------------------ étage 3 : tableau de bord

def tableau(con, jours: int = 90) -> dict:
    depuis = _depuis(jours)

    def taux(groupe: str, filtre_sup: str = "") -> list[dict]:
        # une décision par item : la dernière connue ; version 'corrigée' = retouché
        return rows(con, f"""
            SELECT {groupe} AS cle,
                   COUNT(*) AS relus,
                   SUM(CASE WHEN statut_validation='valide' AND version<>'corrigée' THEN 1 ELSE 0 END) AS valides_directs,
                   SUM(CASE WHEN statut_validation='valide' AND version='corrigée' THEN 1 ELSE 0 END) AS valides_corriges,
                   SUM(CASE WHEN statut_validation='rejete' THEN 1 ELSE 0 END) AS rejetes
            FROM items WHERE statut_validation<>'en_attente' AND date_validation>=? {filtre_sup}
            GROUP BY {groupe} ORDER BY relus DESC""", (depuis,))

    par_discipline = taux("discipline")
    par_epreuve = taux("epreuve_code")
    par_chapitre = [c for c in taux("discipline || ' — ' || COALESCE(chapitre,'?')") if c["relus"] >= 3]
    par_chapitre.sort(key=lambda c: -(c["rejetes"] + 0.5 * c["valides_corriges"]) / c["relus"])
    par_motif = rows(con, """SELECT COALESCE(motif,'Sans motif') cle, COUNT(DISTINCT item_id) n FROM corrections
                             WHERE decision='rejete' AND date>=? GROUP BY motif ORDER BY n DESC""", (depuis,))
    par_motif_disc = rows(con, """SELECT discipline, COALESCE(motif,'Sans motif') motif, COUNT(DISTINCT item_id) n FROM corrections
                                  WHERE decision='rejete' AND date>=? GROUP BY discipline, motif ORDER BY discipline, n DESC""", (depuis,))
    champs = rows(con, """SELECT champ cle, COUNT(*) n FROM corrections WHERE champ IS NOT NULL AND date>=?
                          GROUP BY champ ORDER BY n DESC""", (depuis,))
    for c in champs:
        c["libelle"] = CHAMPS_LISIBLES.get(c["cle"], c["cle"])
    validateurs = rows(con, """SELECT validateur cle, COUNT(DISTINCT item_id) n,
                               SUM(CASE WHEN decision='rejete' THEN 1 ELSE 0 END) rejets FROM corrections
                               WHERE date>=? GROUP BY validateur ORDER BY n DESC""", (depuis,))
    par_lot = rows(con, """SELECT id, cree_le, commande, modele, nb_demandes, nb_recus, erreur
                           FROM lots_generation ORDER BY id DESC LIMIT 12""")
    total = one(con, """SELECT COUNT(*) relus,
                        SUM(CASE WHEN statut_validation='valide' AND version<>'corrigée' THEN 1 ELSE 0 END) valides_directs,
                        SUM(CASE WHEN statut_validation='valide' AND version='corrigée' THEN 1 ELSE 0 END) valides_corriges,
                        SUM(CASE WHEN statut_validation='rejete' THEN 1 ELSE 0 END) rejetes
                        FROM items WHERE statut_validation<>'en_attente' AND date_validation>=?""", (depuis,))
    recents = rows(con, """SELECT item_id, discipline, validateur, date, decision, motif, observations, champ, avant, apres
                           FROM corrections ORDER BY date DESC, id DESC LIMIT 30""")
    return {"jours": jours, "total": total, "par_discipline": par_discipline, "par_epreuve": par_epreuve,
            "par_chapitre": par_chapitre[:15], "par_motif": par_motif, "par_motif_discipline": par_motif_disc,
            "champs_corriges": champs, "validateurs": validateurs, "lots": par_lot, "recents": recents}
