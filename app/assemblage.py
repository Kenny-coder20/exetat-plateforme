"""Assemblage de séries à partir de la banque d'items validés (sans IA)."""
from __future__ import annotations

import random

from .relecture import filtre_publiable
from .db import connect, rows
from .generation import repartition_difficulte

CHAMPS_ELEVE = ("id", "epreuve_code", "discipline", "sous_discipline", "chapitre", "difficulte", "titre", "tige",
                "p1", "p2", "p3", "p4", "p5", "reponse", "correction_detaillee", "erreurs_distracteurs",
                "support", "support_latex", "figure_svg", "figure_legende", "competence", "savoir_essentiel")


def tirer(con, *, discipline: str, sous_discipline: str | None, n: int, chapitre: str | None = None,
          difficulte: str | None = None, graine: int | None = None, exclure: set[str] | None = None,
          epreuve_code: str | None = None) -> list[dict]:
    """Tire n items validés de la banque de l'épreuve, en respectant difficulté et diversité des chapitres."""
    rnd = random.Random(graine)
    exclure = exclure or set()
    sql = f"SELECT * FROM items WHERE {filtre_publiable()} AND situation_id IS NULL AND discipline=?"
    params: list = [discipline]
    if epreuve_code:
        sql += " AND epreuve_code=?"
        params.append(epreuve_code)
    if sous_discipline:
        sql += " AND sous_discipline=?"
        params.append(sous_discipline)
    if chapitre:
        sql += " AND chapitre=?"
        params.append(chapitre)
    pool = [r for r in rows(con, sql, params) if r["id"] not in exclure]
    rnd.shuffle(pool)
    if difficulte:
        cibles = {difficulte: n}
    else:
        cibles = repartition_difficulte(n)
    choisis: list[dict] = []
    chapitres_vus: dict[str, int] = {}

    def prendre(cands, k):
        # privilégie les chapitres les moins représentés
        cands = sorted(cands, key=lambda r: chapitres_vus.get(r["chapitre"], 0))
        pris = cands[:k]
        for r in pris:
            chapitres_vus[r["chapitre"]] = chapitres_vus.get(r["chapitre"], 0) + 1
        return pris

    restants = pool
    for diff, k in cibles.items():
        cands = [r for r in restants if r["difficulte"] == diff]
        pris = prendre(cands, k)
        choisis += pris
        ids = {r["id"] for r in pris}
        restants = [r for r in restants if r["id"] not in ids]
    if len(choisis) < n:  # compléter sans tenir compte de la difficulté
        choisis += prendre(restants, n - len(choisis))
    return choisis


def _epreuve(con, code: str) -> dict:
    ep = con.execute("SELECT * FROM epreuves WHERE code=?", (code,)).fetchone()
    if not ep:
        raise ValueError(f"épreuve {code} inconnue")
    return dict(ep)


def assembler_epreuve(code: str, graine: int | None = None) -> dict:
    with connect() as con:
        ep = _epreuve(con, code)
        quotas = rows(con, "SELECT * FROM quotas WHERE epreuve_code=? ORDER BY ordre", (code,))
        items, manques = [], []
        for q in quotas:
            pris = tirer(con, discipline=q["discipline"], sous_discipline=q["sous_discipline"],
                         n=q["nb_items"], graine=graine, epreuve_code=code)
            if len(pris) < q["nb_items"]:
                manques.append({"discipline": q["discipline"], "sous_discipline": q["sous_discipline"],
                                "manque": q["nb_items"] - len(pris)})
            items += pris
        for k, it in enumerate(items, 1):
            it["numero"] = k
        return {"epreuve": ep, "quotas": quotas, "items": [projeter(i) for i in items], "manques": manques}


def assembler_discipline(code: str, discipline: str, graine: int | None = None) -> dict:
    with connect() as con:
        ep = _epreuve(con, code)
        quotas = rows(con, "SELECT * FROM quotas WHERE epreuve_code=? AND discipline=? ORDER BY ordre", (code, discipline))
        items, manques = [], []
        for q in quotas:
            pris = tirer(con, discipline=q["discipline"], sous_discipline=q["sous_discipline"],
                         n=q["nb_items"], graine=graine, epreuve_code=code)
            if len(pris) < q["nb_items"]:
                manques.append({"sous_discipline": q["sous_discipline"], "manque": q["nb_items"] - len(pris)})
            items += pris
        for k, it in enumerate(items, 1):
            it["numero"] = k
        return {"epreuve": ep, "discipline": discipline, "items": [projeter(i) for i in items], "manques": manques}


def assembler_chapitre(discipline: str, chapitre: str, n: int, difficulte: str | None = None,
                       graine: int | None = None, epreuve_code: str | None = None) -> dict:
    with connect() as con:
        items = tirer(con, discipline=discipline, sous_discipline=None, n=n, chapitre=chapitre,
                      difficulte=difficulte, graine=graine, epreuve_code=epreuve_code)
        for k, it in enumerate(items, 1):
            it["numero"] = k
        return {"discipline": discipline, "chapitre": chapitre, "items": [projeter(i) for i in items],
                "manques": [{"manque": n - len(items)}] if len(items) < n else []}


def projeter(it: dict) -> dict:
    out = {k: it.get(k) for k in CHAMPS_ELEVE}
    out["numero"] = it.get("numero")
    return out


def banque_validee() -> dict:
    """Export complet de la banque validée + configuration : c'est le fichier embarqué par l'app élève."""
    with connect() as con:
        options = rows(con, "SELECT * FROM options ORDER BY code")
        epreuves = rows(con, "SELECT * FROM epreuves ORDER BY code")
        quotas = rows(con, "SELECT * FROM quotas ORDER BY epreuve_code, ordre")
        option_epreuves = rows(con, "SELECT * FROM option_epreuves ORDER BY option_code, jour")
        programme = rows(con, "SELECT discipline, sous_discipline, chapitre, poids, source FROM programme ORDER BY id")
        items = [projeter(i) for i in rows(con, f"SELECT * FROM items WHERE {filtre_publiable()} AND situation_id IS NULL")]
    from .situations import situations_validees
    sits = situations_validees()
    return {"options": options, "epreuves": epreuves, "quotas": quotas, "option_epreuves": option_epreuves,
            "programme": programme, "items": items, "nb_items": len(items), "situations": sits, "nb_situations": len(sits)}
