"""Situations étendues : génération, insertion, assemblage, validation."""
from __future__ import annotations

import uuid
from datetime import datetime

from .assemblage import projeter
from .db import connect, one, rows
from .generation import (MODELE, GenerationError, appeler_modele, compter_mots, inserer_items, repartir_chapitres,
                         verifier_item)

PROMPT_SITUATION = """COMMANDE : génère UNE situation étendue (exercice de synthèse) en {discipline}{sd}, option 1.02 Sciences,
centrée sur le chapitre « {chapitre} »{autres}, suivie de {n} questions QCM qui en découlent.

RÈGLES DU FORMAT « SITUATION ÉTENDUE » (elles s'ajoutent à la charte et au cahier des charges)
- Situation de 150 à 300 mots : un acteur, un lieu congolais réel, un problème concret à résoudre, toutes les données
  numériques nécessaires avec leurs unités, regroupées dans un DOCUMENT (tableau de données, fiche technique, schéma,
  graphique). Décris le document en LaTeX (tabular, TikZ ou pgfplots) dans `document_latex` ET en texte lisible dans
  `document_texte`.
- {n} questions de difficulté croissante : d'abord identifier ou extraire (facile), puis calculer ou appliquer (moyen),
  enfin interpréter, comparer ou décider (difficile). La dernière question conclut sur le problème posé.
- Chaque question est répondable sans la réponse de la précédente : si un résultat intermédiaire est réutilisé, rappelle-le
  dans l'énoncé (« on admet que … »). Une erreur ne doit pas en entraîner une autre.
- Chaque question : énoncé direct de 15 à 45 mots (le contexte est déjà posé), 5 propositions numérotées 1 à 5, une seule
  correcte, distracteurs reliés à des erreurs plausibles, correction détaillée.
- Deux à trois chapitres du programme reliés par la situation, pas davantage.
- Termine par une `synthese` de 3 à 5 lignes qui répond au problème de la situation.
- Varie la position de la bonne réponse.

FORMAT DE SORTIE : uniquement un objet JSON :
{{"situation": {{"titre": "...", "texte": "...", "document_texte": "...", "document_latex": "... ou null",
  "chapitres": "chap. 1 ; chap. 2", "duree_min": 25, "synthese": "..."}},
 "items": [ {{ "ordre": 1, "discipline": "{discipline}", "sous_discipline": "... ou null", "chapitre": "...", "savoir_essentiel": "...",
   "competence": "calculer|modéliser|raisonner|analyser|interpréter|transférer", "difficulte": "facile|moyen|difficile",
   "famille_contexte": "...", "support": "aucun", "support_latex": null, "titre": "Q1 — ...", "tige": "...",
   "propositions": ["...", "...", "...", "...", "..."], "reponse": 1, "correction_detaillee": "...",
   "erreurs_distracteurs": "...", "observations": null }} ] }}"""


def composer_commande_situation(con, discipline, sous_discipline, chapitre, n):
    if not chapitre:
        chaps = repartir_chapitres(con, discipline, sous_discipline, 3)
        chapitre, autres = chaps[0], [c for c in chaps[1:] if c != chaps[0]]
    else:
        autres = [c for c in repartir_chapitres(con, discipline, sous_discipline, 4) if c != chapitre][:2]
    return PROMPT_SITUATION.format(
        discipline=discipline, sd=f" ({sous_discipline})" if sous_discipline else "", chapitre=chapitre, n=n,
        autres=(" en lien avec « " + " » et « ".join(autres) + " »") if autres else "")


def verifier_situation(s: dict) -> list[str]:
    pb = []
    nb = compter_mots(s.get("texte", ""))
    s["nb_mots"] = nb
    if nb < 120:
        pb.append(f"situation trop courte ({nb} mots)")
    if nb > 330:
        pb.append(f"situation trop longue ({nb} mots)")
    for c in ("titre", "texte", "document_texte", "synthese"):
        if not s.get(c):
            pb.append(f"champ manquant : {c}")
    return pb


def inserer_situation(con, data: dict, *, discipline: str, sous_discipline: str | None, modele=MODELE,
                      option_code=None, epreuve_code: str | None = None) -> str:
    s = data.get("situation") or {}
    items = data.get("items") or []
    anomalies = verifier_situation(s)
    if not 3 <= len(items) <= 7:
        anomalies.append(f"{len(items)} questions (attendu 4 à 6)")
    diffs = [it.get("difficulte") for it in items]
    ordre = {"facile": 0, "moyen": 1, "difficile": 2}
    if diffs != sorted(diffs, key=lambda d: ordre.get(d, 1)):
        anomalies.append("difficulté non croissante")
    obs = ("ANOMALIES AUTO : " + " ; ".join(anomalies)) if anomalies else None
    sid = f"SIT-{uuid.uuid4().hex[:8]}"
    con.execute(
        """INSERT INTO situations(id, option_code, epreuve_code, discipline, sous_discipline, chapitres, titre, texte, document_texte,
           document_latex, synthese, duree_min, nb_mots, modele, observations) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (sid, option_code, epreuve_code, discipline, sous_discipline, s.get("chapitres"), s.get("titre", "Situation"), s.get("texte", ""),
         s.get("document_texte"), s.get("document_latex"), s.get("synthese"), int(s.get("duree_min") or 25),
         s.get("nb_mots"), modele, obs))
    for k, it in enumerate(items, 1):
        it.setdefault("discipline", discipline)
        it.setdefault("famille_contexte", "situation étendue")
        it["tige"] = it.get("tige", "")
    ids = inserer_items(con, items, option_code=option_code, epreuve_code=epreuve_code, modele=modele)
    for k, iid in enumerate(ids, 1):
        con.execute("UPDATE items SET situation_id=?, ordre_situation=? WHERE id=?", (sid, k, iid))
        # pour une question de situation, la tige peut être courte : on neutralise l'anomalie « trop courte »
        it = one(con, "SELECT observations, nb_mots_tige FROM items WHERE id=?", (iid,))
        if it["observations"] and "tige trop courte" in it["observations"] and (it["nb_mots_tige"] or 0) >= 12:
            nouv = it["observations"].replace(f"tige trop courte ({it['nb_mots_tige']} mots)", "").replace(" ;  ;", " ;")
            nouv = nouv.replace("ANOMALIES AUTO :  ; ", "ANOMALIES AUTO : ").replace("ANOMALIES AUTO : . ", "").strip(" ;.")
            con.execute("UPDATE items SET observations=? WHERE id=?", (nouv or None, iid))
    return sid


def generer_situation(*, discipline: str, sous_discipline: str | None = None, chapitre: str | None = None,
                      n: int = 5, epreuve_code: str | None = None) -> dict:
    with connect() as con:
        commande = composer_commande_situation(con, discipline, sous_discipline, chapitre, n)
        lot = con.execute("INSERT INTO lots_generation(commande, modele, nb_demandes) VALUES(?,?,?)",
                          (commande, MODELE, n)).lastrowid
        try:
            data, usage = appeler_modele(commande, max_tokens=12000)
        except Exception as e:  # noqa: BLE001
            con.execute("UPDATE lots_generation SET erreur=? WHERE id=?", (str(e), lot))
            raise
        sid = inserer_situation(con, data, discipline=discipline, sous_discipline=sous_discipline, epreuve_code=epreuve_code)
        con.execute("UPDATE lots_generation SET nb_recus=?, cout_tokens_in=?, cout_tokens_out=? WHERE id=?",
                    (len(data.get("items", [])), usage["in"], usage["out"], lot))
        return {"lot": lot, "situation_id": sid, "nb_questions": len(data.get("items", [])), "usage": usage}


# ---------------------------------------------------------------- lecture / validation

def lire_situation(con, sid: str) -> dict | None:
    s = one(con, "SELECT * FROM situations WHERE id=?", (sid,))
    if not s:
        return None
    s["questions"] = rows(con, "SELECT * FROM items WHERE situation_id=? ORDER BY ordre_situation", (sid,))
    return s


def lister_situations(con, statut: str | None = None, discipline: str | None = None, epreuve_code: str | None = None) -> list[dict]:
    sql = ("SELECT s.*, (SELECT COUNT(*) FROM items i WHERE i.situation_id=s.id) nb_questions, "
           "(SELECT COUNT(*) FROM items i WHERE i.situation_id=s.id AND i.statut_validation='valide') nb_validees "
           "FROM situations s WHERE 1=1")
    p: list = []
    if statut:
        sql += " AND s.statut_validation=?"; p.append(statut)
    if discipline:
        sql += " AND s.discipline=?"; p.append(discipline)
    if epreuve_code:
        sql += " AND s.epreuve_code=?"; p.append(epreuve_code)
    return rows(con, sql + " ORDER BY s.cree_le DESC", p)


def statuer_situation(con, sid: str, statut: str, validateur: str, observations: str | None, motif: str | None,
                      champs: dict) -> dict:
    for k, v in champs.items():
        if k in ("titre", "texte", "document_texte", "document_latex", "synthese", "chapitres", "duree_min"):
            con.execute(f"UPDATE situations SET {k}=?, version='corrigée' WHERE id=?", (v, sid))
    if "texte" in champs:
        con.execute("UPDATE situations SET nb_mots=? WHERE id=?", (compter_mots(champs["texte"]), sid))
    if statut == "valide":
        nv = one(con, "SELECT COUNT(*) n FROM items WHERE situation_id=? AND statut_validation!='valide'", (sid,))["n"]
        if nv:
            raise GenerationError(f"{nv} question(s) de cette situation ne sont pas encore validées.")
    if statut == "rejete":
        con.execute("UPDATE items SET statut_validation='rejete', motif_rejet=COALESCE(motif_rejet,'situation rejetée') "
                    "WHERE situation_id=? AND statut_validation='en_attente'", (sid,))
    con.execute("UPDATE situations SET statut_validation=?, validateur=?, date_validation=?, observations=?, motif_rejet=? "
                "WHERE id=?", (statut, validateur, datetime.now().isoformat(timespec="minutes"), observations, motif, sid))
    return lire_situation(con, sid)


# ---------------------------------------------------------------- élève

def projeter_situation(s: dict) -> dict:
    return {k: s.get(k) for k in ("id", "epreuve_code", "discipline", "sous_discipline", "chapitres", "titre", "texte", "document_texte",
                                  "document_latex", "synthese", "duree_min")} | {
        "questions": [projeter(q) | {"numero": q.get("ordre_situation")} for q in s.get("questions", [])]}


def situations_validees() -> list[dict]:
    with connect() as con:
        out = []
        for s in rows(con, "SELECT * FROM situations WHERE statut_validation='valide' ORDER BY discipline, titre"):
            s["questions"] = rows(con, "SELECT * FROM items WHERE situation_id=? AND statut_validation='valide' "
                                       "ORDER BY ordre_situation", (s["id"],))
            if s["questions"]:
                out.append(projeter_situation(s))
        return out
