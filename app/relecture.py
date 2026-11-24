"""Relecture à l'aveugle : l'enseignant choisit la bonne réponse AVANT de voir la clé.

Le désaccord entre un enseignant et la clé est d'abord un signal sur l'item (clé fausse, ambiguïté), ensuite seulement
un signal sur le relecteur. La « performance » d'un enseignant se mesure donc par rapport à la CLÉ FINALE (après
corrections), et un désaccord suivi d'une correction de la clé compte comme une détection, à son crédit.

Publication : un item validé n'est embarqué dans l'application élève que s'il a reçu RELECTURES_REQUISES relectures
concordantes avec sa clé finale, par des enseignants distincts (défaut 1 ; 2 = double relecture). Les items validés
sans aucune relecture à l'aveugle (banque antérieure au dispositif, import) restent publiés.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from .db import one, rows

VERDICTS = ("erreur_relecteur", "cle_fausse", "ambigu")
VERDICTS_LIBELLES = {"erreur_relecteur": "je m'étais trompé(e)", "cle_fausse": "la clé est fausse", "ambigu": "deux réponses défendables"}


def relectures_requises() -> int:
    try:
        return max(0, int(os.environ.get("RELECTURES_REQUISES", "1")))
    except ValueError:
        return 1


# ------------------------------------------------------------------ enregistrement

def enregistrer(con, *, item: dict, validateur: str, nom: str, reponse: int, duree_s: int | None) -> dict:
    if reponse not in (1, 2, 3, 4, 5):
        raise ValueError("réponse entre 1 et 5")
    cle = int(item["reponse"])
    concordant = 1 if reponse == cle else 0
    cur = con.execute(
        "INSERT INTO relectures(item_id, validateur, nom, discipline, epreuve_code, reponse_donnee, cle_affichee, concordant, duree_s, date) "
        "VALUES(?,?,?,?,?,?,?,?,?,?)",
        (item["id"], validateur, nom, item.get("discipline"), item.get("epreuve_code"), reponse, cle, concordant, duree_s,
         datetime.now().isoformat(timespec="seconds")))
    return {"id": cur.lastrowid, "cle": cle, "concordant": bool(concordant), "reponse_donnee": reponse}


def verdict(con, rid: int, validateur: str, v: str) -> None:
    if v not in VERDICTS:
        raise ValueError("verdict invalide")
    con.execute("UPDATE relectures SET verdict=? WHERE id=? AND validateur=?", (v, rid, validateur))


def deja_relu(con, item_id: str, validateur: str) -> dict | None:
    return one(con, "SELECT * FROM relectures WHERE item_id=? AND validateur=? ORDER BY id DESC LIMIT 1", (item_id, validateur))


# ------------------------------------------------------------------ publication

def etat_publication(con, item_id: str) -> dict:
    """Combien de relecteurs distincts concordent avec la clé actuelle, et combien il en faut."""
    it = one(con, "SELECT reponse, statut_validation FROM items WHERE id=?", (item_id,))
    req = relectures_requises()
    if not it:
        return {"requis": req, "concordants": 0, "total": 0, "publiable": False}
    r = one(con, "SELECT COUNT(DISTINCT validateur) AS n FROM relectures WHERE item_id=? AND reponse_donnee=?", (item_id, it["reponse"]))
    t = one(con, "SELECT COUNT(DISTINCT validateur) AS n FROM relectures WHERE item_id=?", (item_id,))
    n, tot = r["n"], t["n"]
    return {"requis": req, "concordants": n, "total": tot,
            "publiable": it["statut_validation"] == "valide" and (req == 0 or tot == 0 or n >= req)}


def filtre_publiable() -> str:
    """Fragment SQL (sur l'alias implicite de la table items) : items validés ET suffisamment relus."""
    req = relectures_requises()
    if req == 0:
        return "statut_validation='valide'"
    return ("statut_validation='valide' AND ("
            "NOT EXISTS (SELECT 1 FROM relectures r WHERE r.item_id=items.id) OR "
            f"(SELECT COUNT(DISTINCT r.validateur) FROM relectures r WHERE r.item_id=items.id AND r.reponse_donnee=items.reponse) >= {req})")


# ------------------------------------------------------------------ indicateurs

def _depuis(jours: int) -> str:
    return (datetime.now() - timedelta(days=jours)).isoformat(timespec="seconds")


def _stats(con, filtre: str, params: list) -> list[dict]:
    """Par relecteur : relectures, concordance avec la clé affichée, concordance avec la clé finale, détections, temps médian."""
    base = rows(con, f"""
        SELECT r.validateur, MAX(r.nom) AS nom, r.discipline,
               COUNT(*) AS relectures,
               SUM(r.concordant) AS concordants_affiche,
               SUM(CASE WHEN r.reponse_donnee = i.reponse THEN 1 ELSE 0 END) AS concordants_final,
               SUM(CASE WHEN r.concordant=0 AND i.reponse <> r.cle_affichee THEN 1 ELSE 0 END) AS detections_cle,
               SUM(CASE WHEN r.concordant=0 AND i.statut_validation='rejete' THEN 1 ELSE 0 END) AS detections_rejet,
               SUM(CASE WHEN r.verdict='erreur_relecteur' THEN 1 ELSE 0 END) AS erreurs_reconnues,
               SUM(CASE WHEN r.verdict='ambigu' THEN 1 ELSE 0 END) AS ambigus,
               SUM(CASE WHEN r.duree_s IS NOT NULL AND r.duree_s < 8 THEN 1 ELSE 0 END) AS trop_rapides
        FROM relectures r JOIN items i ON i.id = r.item_id
        WHERE {filtre} GROUP BY r.validateur, r.discipline ORDER BY r.validateur, relectures DESC""", params)
    durees: dict[tuple, list[int]] = {}
    for d in rows(con, f"SELECT r.validateur, r.discipline, r.duree_s FROM relectures r JOIN items i ON i.id=r.item_id WHERE {filtre} AND r.duree_s IS NOT NULL", params):
        durees.setdefault((d["validateur"], d["discipline"]), []).append(d["duree_s"])
    for b in base:
        ds = sorted(durees.get((b["validateur"], b["discipline"]), []))
        b["duree_mediane_s"] = ds[len(ds) // 2] if ds else None
        n = b["relectures"] or 0
        b["taux_concordance_final"] = round(100 * (b["concordants_final"] or 0) / n) if n else None
        b["detections"] = (b["detections_cle"] or 0) + (b["detections_rejet"] or 0)
    return base


def _agreger(lignes: list[dict]) -> list[dict]:
    """Regroupe les lignes par relecteur (toutes disciplines) en gardant le détail par discipline."""
    out: dict[str, dict] = {}
    for l in lignes:
        a = out.setdefault(l["validateur"], {"validateur": l["validateur"], "nom": l["nom"], "relectures": 0, "concordants_final": 0,
                                             "detections": 0, "erreurs_reconnues": 0, "ambigus": 0, "trop_rapides": 0, "durees": [], "disciplines": []})
        for k in ("relectures", "concordants_final", "detections", "erreurs_reconnues", "ambigus", "trop_rapides"):
            a[k] += l[k] or 0
        if l["duree_mediane_s"] is not None:
            a["durees"] += [l["duree_mediane_s"]] * (l["relectures"] or 1)
        a["disciplines"].append({"discipline": l["discipline"], "relectures": l["relectures"], "taux_concordance_final": l["taux_concordance_final"],
                                 "detections": l["detections"]})
    for a in out.values():
        n = a["relectures"]
        a["taux_concordance_final"] = round(100 * a["concordants_final"] / n) if n else None
        ds = sorted(a.pop("durees"))
        a["duree_mediane_s"] = ds[len(ds) // 2] if ds else None
    return sorted(out.values(), key=lambda a: -a["relectures"])


def tableau_relecteurs(con, jours: int = 90) -> list[dict]:
    return _agreger(_stats(con, "r.date>=?", [_depuis(jours)]))


def mes_relectures(con, validateur: str, jours: int = 90) -> dict:
    lignes = _agreger(_stats(con, "r.validateur=? AND r.date>=?", [validateur, _depuis(jours)]))
    moi = lignes[0] if lignes else {"validateur": validateur, "relectures": 0, "concordants_final": 0, "detections": 0, "erreurs_reconnues": 0,
                                    "ambigus": 0, "trop_rapides": 0, "taux_concordance_final": None, "duree_mediane_s": None, "disciplines": []}
    moi["jours"] = jours
    moi["dernieres"] = rows(con, """SELECT r.date, r.item_id, r.discipline, r.reponse_donnee, r.cle_affichee, r.concordant, r.verdict, r.duree_s,
                                           i.reponse AS cle_finale, i.statut_validation, i.titre
                                    FROM relectures r JOIN items i ON i.id=r.item_id WHERE r.validateur=? ORDER BY r.id DESC LIMIT 12""", (validateur,))
    return moi


def items_suspects(con, jours: int = 90, limite: int = 15) -> list[dict]:
    """Items validés ou en attente dont au moins un relecteur a contredit la clé finale : à faire relire en priorité."""
    return rows(con, """SELECT i.id, i.titre, i.discipline, i.statut_validation, i.reponse,
                               COUNT(*) AS relectures,
                               SUM(CASE WHEN r.reponse_donnee <> i.reponse THEN 1 ELSE 0 END) AS desaccords,
                               SUM(CASE WHEN r.verdict='ambigu' THEN 1 ELSE 0 END) AS ambigus
                        FROM items i JOIN relectures r ON r.item_id=i.id
                        WHERE i.statut_validation <> 'rejete' AND r.date>=?
                        GROUP BY i.id, i.titre, i.discipline, i.statut_validation, i.reponse
                        HAVING SUM(CASE WHEN r.reponse_donnee <> i.reponse THEN 1 ELSE 0 END) > 0
                        ORDER BY desaccords DESC, relectures DESC LIMIT ?""", (_depuis(jours), limite))
