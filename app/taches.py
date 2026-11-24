"""Tâches de génération en arrière-plan : lancement immédiat, suivi par sondage.

Les travaux tournent dans des threads du processus web (suffisant pour un atelier de quelques validateurs).
Les quotas d'une épreuve sont générés en parallèle, puis insérés dans l'ordre du E.32.
"""
from __future__ import annotations

import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from . import generation, situations

_TACHES: dict[str, dict] = {}
_VERROU = threading.Lock()


def _maj(tid: str, **champs):
    with _VERROU:
        _TACHES[tid].update(champs)
        _TACHES[tid]["maj"] = time.time()


def etat(tid: str) -> dict | None:
    with _VERROU:
        t = _TACHES.get(tid)
        return dict(t) if t else None


def liste() -> list[dict]:
    with _VERROU:
        return sorted((dict(t) for t in _TACHES.values()), key=lambda t: -t["debut"])[:20]


def _lancer(libelle: str, cible, *args, **kwargs) -> str:
    tid = uuid.uuid4().hex[:8]
    with _VERROU:
        _TACHES[tid] = {"id": tid, "libelle": libelle, "statut": "en_cours", "etapes": [], "debut": time.time(),
                        "maj": time.time(), "resultat": None, "erreur": None}

    def run():
        try:
            res = cible(tid, *args, **kwargs)
            _maj(tid, statut="termine", resultat=res)
        except Exception as e:  # noqa: BLE001
            _maj(tid, statut="erreur", erreur=f"{type(e).__name__} : {e}")

    threading.Thread(target=run, daemon=True).start()
    return tid


def _etape(tid: str, texte: str):
    with _VERROU:
        _TACHES[tid]["etapes"].append({"t": time.time(), "texte": texte})
        _TACHES[tid]["maj"] = time.time()


# ------------------------------------------------------------------ travaux

def _travail_epreuve(tid: str, jour: int, serie: str | None):
    from .db import connect, rows

    with connect() as con:
        ep = con.execute("SELECT * FROM epreuves WHERE option_code='1.02' AND jour=?", (jour,)).fetchone()
        if not ep or not ep["actif"]:
            raise generation.GenerationError(f"Épreuve du jour {jour} indisponible.")
        quotas = rows(con, "SELECT * FROM quotas WHERE epreuve_id=? ORDER BY ordre", (ep["id"],))
    _etape(tid, f"{len(quotas)} appels lancés en parallèle pour {ep['code']}")
    numero, departs = 1, []
    for q in quotas:
        departs.append(numero)
        numero += q["nb_items"]

    def un(q, dep):
        nom = q["discipline"] + (f" / {q['sous_discipline']}" if q["sous_discipline"] else "")
        try:
            r = generation.generer(discipline=q["discipline"], sous_discipline=q["sous_discipline"], n=q["nb_items"],
                                   jour=jour, serie=serie, epreuve_code=ep["code"], numero_depart=dep)
            _etape(tid, f"{nom} : {len(r['ids'])}/{q['nb_items']} items reçus")
            return {"quota": nom, "nb": len(r["ids"]), "usage": r["usage"], "anomalies": r["anomalies_serie"]}
        except Exception as e:  # noqa: BLE001
            _etape(tid, f"{nom} : ÉCHEC — {e}")
            return {"quota": nom, "nb": 0, "erreur": str(e)}

    with ThreadPoolExecutor(max_workers=min(4, len(quotas))) as ex:
        res = list(ex.map(lambda qd: un(*qd), zip(quotas, departs)))
    total = sum(r["nb"] for r in res)
    _etape(tid, f"Terminé : {total} items en attente de validation")
    return {"lots": res, "total": total}


def _travail_items(tid: str, **kw):
    _etape(tid, f"Génération de {kw.get('n')} items de {kw.get('discipline')}")
    r = generation.generer(**kw)
    _etape(tid, f"{len(r['ids'])} items reçus")
    return {"nb": len(r["ids"]), "usage": r["usage"], "anomalies": r["anomalies_serie"]}


def _travail_situation(tid: str, **kw):
    _etape(tid, f"Génération d'une situation étendue en {kw.get('discipline')}")
    r = situations.generer_situation(**kw)
    _etape(tid, f"Situation {r['situation_id']} : {r['nb_questions']} questions")
    return r


def lancer_epreuve(jour: int, serie: str | None = None) -> str:
    return _lancer(f"Épreuve du jour {jour}" + (f", série {serie}" if serie else ""), _travail_epreuve, jour, serie)


def lancer_items(**kw) -> str:
    return _lancer(f"{kw.get('n')} items — {kw.get('discipline')}", _travail_items, **kw)


def lancer_situation(**kw) -> str:
    return _lancer(f"Situation étendue — {kw.get('discipline')}", _travail_situation, **kw)
