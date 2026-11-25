"""Outils communs aux lots préparés : mélange des propositions, chapitres du programme, contextes, écriture."""
from __future__ import annotations

import json
import math
import os
import random
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
os.environ.setdefault("EXETAT_DB", "/tmp/lots_prog.db")
from app.db import connect, preparer, rows  # noqa: E402

_PROG: dict[str, list[str]] | None = None


def programme() -> dict[str, list[str]]:
    """Chapitres par discipline, tels qu'ils figurent sur la plateforme (après complément)."""
    global _PROG
    if _PROG is None:
        preparer(demo_si_vide=False)
        _PROG = {}
        with connect() as con:
            for r in rows(con, "SELECT discipline, sous_discipline, chapitre FROM programme ORDER BY id"):
                _PROG.setdefault(r["discipline"], []).append(r["chapitre"])
                if r["sous_discipline"]:
                    _PROG.setdefault(r["sous_discipline"], []).append(r["chapitre"])
    return _PROG


def chapitre(discipline: str, *mots: str) -> str:
    """Le chapitre du programme dont l'intitulé contient le plus de mots-clés donnés (sinon le premier)."""
    chs = programme().get(discipline) or []
    if not chs:
        return mots[0] if mots else discipline
    def score(c):
        cl = c.lower()
        return sum(1 for m in mots if m.lower() in cl)
    best = max(chs, key=score)
    return best if score(best) > 0 else chs[0]


def fmt(v: float, d: int = 2) -> str:
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    s = f"{v:.{d}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("-0", "-"):
        s = "0"
    return s.replace(".", ",")


def melanger(it: dict, rnd: random.Random) -> None:
    """Permute les propositions, met à jour la réponse et renumérote les erreurs des distracteurs."""
    perm = list(range(5))
    rnd.shuffle(perm)
    props = [it["propositions"][perm[j]] for j in range(5)]
    nouveau = {perm[j] + 1: j + 1 for j in range(5)}
    it["propositions"] = props
    it["reponse"] = nouveau[it["reponse"]]
    parts = []
    for part in re.split(r"\s;\s", it.get("erreurs_distracteurs") or ""):
        m = re.match(r"^\s*([\d,\s]+(?:et\s*\d)?)\s*:\s*(.*)$", part)
        if not m:
            if part.strip():
                parts.append((99, part.strip()))
            continue
        nums = [int(x) for x in re.findall(r"\d", m.group(1))]
        nn = sorted(nouveau[n] for n in nums if n in nouveau)
        if not nn:
            continue
        lab = " et ".join(map(str, nn)) if len(nn) <= 2 else ", ".join(map(str, nn))
        parts.append((nn[0], f"{lab} : {m.group(2).strip().rstrip('.')}"))
    it["erreurs_distracteurs"] = " ; ".join(t for _, t in sorted(parts, key=lambda x: x[0])) + ("." if parts else "")


def distracteurs(bonne: float, rnd: random.Random, *, unite: str = "", d: int = 2, facteurs=(0.5, 2, 1.5, 0.1, 10, 0.75, 1.25), additifs=()) -> list[str]:
    """Quatre valeurs plausibles distinctes autour de la bonne (facteurs d'erreur classiques), formatées."""
    cands = []
    for f in facteurs:
        cands.append(bonne * f)
    for a in additifs:
        cands.append(bonne + a)
    rnd.shuffle(cands)
    out, vus = [], {fmt(bonne, d)}
    for c in cands:
        s = fmt(c, d)
        if s not in vus and c > 0:
            vus.add(s)
            out.append(s)
        if len(out) == 4:
            break
    while len(out) < 4:
        c = bonne * (1 + rnd.choice([-0.3, 0.3, -0.6, 0.6, 3]))
        s = fmt(c, d)
        if s not in vus:
            vus.add(s)
            out.append(s)
    return [o + unite for o in out]


_NUM = re.compile(r"-?\d+(?:,\d+)?")


def reparer_doublons(bonne: str, faux: list[str], rnd: random.Random) -> list[str]:
    """Remplace les distracteurs en double (ou égaux à la bonne réponse) par des valeurs voisines quand ils contiennent un nombre."""
    vus, out = {bonne}, []
    mb = _NUM.search(bonne)
    base = float(mb.group(0).replace(",", ".")) if mb else None
    for f in faux:
        if f not in vus:
            vus.add(f); out.append(f); continue
        m = _NUM.search(f)
        if not m or base is None:
            continue
        d = len(m.group(0).split(",")[1]) if "," in m.group(0) else 0
        for fac in (3, 0.25, 4, 1.8, 0.6, 2.5, 6, 0.15, -1, 7):
            v = base * fac if base != 0 else fac
            c = f[:m.start()] + fmt(v, d) + f[m.end():]
            if c not in vus:
                vus.add(c); out.append(c); break
    return out


def item(*, id_: str, discipline: str, sous: str | None, epreuve: str, chap: str, difficulte: str, type_item: str, competence: str,
         savoir: str, famille: str, titre: str, tige: str, bonne: str, faux: list[str], correction: str, erreurs: list[str],
         figure: str, legende: str, rnd: random.Random) -> dict:
    faux = reparer_doublons(bonne, faux, rnd)
    assert len(faux) == 4 and len({bonne, *faux}) == 5, (id_, bonne, faux)
    nb = len(tige.split())
    assert 28 <= nb <= 110, f"{id_} : {nb} mots"
    it = {
        "id": id_, "discipline": discipline, "sous_discipline": sous, "epreuve_code": epreuve, "chapitre": chap,
        "savoir_essentiel": savoir, "competence": competence, "difficulte": difficulte, "type_item": type_item, "famille_contexte": famille,
        "support": "figure", "titre": titre, "tige": tige, "propositions": [bonne] + faux, "reponse": 1,
        "correction_detaillee": correction, "erreurs_distracteurs": " ; ".join(f"{k + 2} : {e}" for k, e in enumerate(erreurs)) + ".",
        "nb_mots_tige": nb, "figure_svg": figure, "figure_legende": legende,
    }
    melanger(it, rnd)
    return it


def ecrire_lot(nom: str, items: list[dict], source: str) -> Path:
    out = RACINE / "lots" / f"{nom}.json"
    out.write_text(json.dumps({"source": source, "items": items}, ensure_ascii=False, indent=0), encoding="utf-8")
    return out
