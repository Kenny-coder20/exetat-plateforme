"""API FastAPI + interfaces statiques (validateur, élève)."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import assemblage, export, generation, situations
from .db import connect, one, preparer, rows
import os
import secrets
from fastapi import Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

app = FastAPI(title="Plateforme items EXETAT", version="0.2")

# ------------------------------------------------------------------ protection de l'atelier
# Définissez ATELIER_MOT_DE_PASSE (et éventuellement ATELIER_UTILISATEUR) pour protéger l'atelier
# et les opérations d'écriture : indispensable dès que la plateforme est accessible sur Internet.
ATELIER_UTILISATEUR = os.environ.get("ATELIER_UTILISATEUR", "atelier")
ATELIER_MOT_DE_PASSE = os.environ.get("ATELIER_MOT_DE_PASSE", "")
PREFIXES_PROTEGES = ("/validateur", "/api/generer", "/api/importer", "/api/situations/generer", "/api/export/", "/docs", "/openapi.json")
import base64
from starlette.responses import Response


@app.middleware("http")
async def _proteger_atelier(request: Request, call_next):
    if ATELIER_MOT_DE_PASSE:
        chemin = request.url.path
        protege = chemin.startswith(PREFIXES_PROTEGES) or chemin.endswith("/valider") or (
            chemin.startswith("/api/items") and request.method != "GET") or (
            chemin.startswith("/api/situations") and request.method != "GET" and not chemin.endswith("/generer"))
        if protege:
            ok = False
            auth = request.headers.get("authorization", "")
            if auth.lower().startswith("basic "):
                try:
                    u, _, p = base64.b64decode(auth[6:]).decode("utf-8").partition(":")
                    ok = secrets.compare_digest(u, ATELIER_UTILISATEUR) and secrets.compare_digest(p, ATELIER_MOT_DE_PASSE)
                except Exception:  # noqa: BLE001
                    ok = False
            if not ok:
                return Response("Accès réservé à l'atelier.", status_code=401,
                                headers={"WWW-Authenticate": 'Basic realm="Atelier EXETAT"'})
    return await call_next(request)


@app.on_event("startup")
def _startup():
    preparer(demo_si_vide=os.environ.get("EXETAT_DEMO", "1") == "1")


@app.get("/", include_in_schema=False)
def accueil():
    return FileResponse(STATIC / "accueil.html", media_type="text/html")


# ------------------------------------------------------------------ configuration

@app.get("/api/config")
def config():
    with connect() as con:
        return {
            "options": rows(con, "SELECT * FROM options"),
            "epreuves": rows(con, "SELECT * FROM epreuves ORDER BY option_code, jour"),
            "quotas": rows(con, "SELECT q.*, e.option_code, e.jour FROM quotas q JOIN epreuves e ON e.id=q.epreuve_id ORDER BY e.jour, q.ordre"),
            "programme": rows(con, "SELECT * FROM programme ORDER BY discipline, sous_discipline, id"),
        }


@app.get("/api/stats")
def stats():
    with connect() as con:
        return {
            "par_statut": rows(con, "SELECT statut_validation statut, COUNT(*) n FROM items WHERE situation_id IS NULL GROUP BY 1"),
            "par_discipline": rows(con, "SELECT discipline, COALESCE(sous_discipline,'') sous_discipline, statut_validation statut, COUNT(*) n FROM items WHERE situation_id IS NULL GROUP BY 1,2,3 ORDER BY 1,2,3"),
            "situations": rows(con, "SELECT statut_validation statut, COUNT(*) n FROM situations GROUP BY 1"),
            "par_chapitre_valide": rows(con, "SELECT discipline, chapitre, difficulte, COUNT(*) n FROM items WHERE statut_validation='valide' GROUP BY 1,2,3 ORDER BY 1,2,3"),
            "lots": rows(con, "SELECT * FROM lots_generation ORDER BY id DESC LIMIT 20"),
            "resultats": rows(con, "SELECT mode, COUNT(*) n, ROUND(AVG(100.0*score/nb_items),1) pct FROM resultats GROUP BY 1"),
        }


# ------------------------------------------------------------------ items (atelier)

@app.get("/api/items")
def lister_items(statut: Optional[str] = None, discipline: Optional[str] = None, limite: int = 200,
                 situation: Optional[str] = None):
    sql, p = "SELECT * FROM items WHERE 1=1", []
    if situation:
        sql += " AND situation_id=?"; p.append(situation)
    else:
        sql += " AND situation_id IS NULL"
    if statut:
        sql += " AND statut_validation=?"; p.append(statut)
    if discipline:
        sql += " AND discipline=?"; p.append(discipline)
    sql += " ORDER BY cree_le DESC, numero LIMIT ?"; p.append(limite)
    with connect() as con:
        return rows(con, sql, p)


@app.get("/api/items/{iid}")
def lire_item(iid: str):
    with connect() as con:
        it = one(con, "SELECT * FROM items WHERE id=?", (iid,))
        if it and it.get("situation_id"):
            it["situation"] = one(con, "SELECT * FROM situations WHERE id=?", (it["situation_id"],))
    if not it:
        raise HTTPException(404)
    return it


# ------------------------------------------------------------------ situations étendues

class CommandeSituation(BaseModel):
    discipline: str
    sous_discipline: Optional[str] = None
    chapitre: Optional[str] = None
    n: int = 5


@app.post("/api/situations/generer")
def api_generer_situation(c: CommandeSituation):
    try:
        return situations.generer_situation(discipline=c.discipline, sous_discipline=c.sous_discipline,
                                            chapitre=c.chapitre, n=max(3, min(7, c.n)))
    except generation.GenerationError as e:
        raise HTTPException(400, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Erreur interne pendant la génération : {type(e).__name__} : {e}")


@app.get("/api/situations")
def api_lister_situations(statut: Optional[str] = None, discipline: Optional[str] = None):
    with connect() as con:
        return situations.lister_situations(con, statut, discipline)


@app.get("/api/situations/validees")
def api_situations_validees():
    return situations.situations_validees()


@app.get("/api/situations/{sid}")
def api_lire_situation(sid: str):
    with connect() as con:
        s = situations.lire_situation(con, sid)
    if not s:
        raise HTTPException(404)
    return s


class ValidationSituation(BaseModel):
    statut: str
    validateur: str = ""
    observations: Optional[str] = None
    motif_rejet: Optional[str] = None
    titre: Optional[str] = None
    texte: Optional[str] = None
    document_texte: Optional[str] = None
    document_latex: Optional[str] = None
    synthese: Optional[str] = None
    chapitres: Optional[str] = None
    duree_min: Optional[int] = None


@app.post("/api/situations/{sid}/valider")
def api_valider_situation(sid: str, v: ValidationSituation):
    champs = {k: getattr(v, k) for k in ("titre", "texte", "document_texte", "document_latex", "synthese", "chapitres", "duree_min")
              if getattr(v, k) is not None}
    try:
        with connect() as con:
            if not one(con, "SELECT id FROM situations WHERE id=?", (sid,)):
                raise HTTPException(404)
            return situations.statuer_situation(con, sid, v.statut, v.validateur or "anonyme", v.observations, v.motif_rejet, champs)
    except generation.GenerationError as e:
        raise HTTPException(400, str(e))


@app.get("/api/export/situation/{sid}")
def api_export_situation(sid: str, pdf: bool = False):
    with connect() as con:
        s = situations.lire_situation(con, sid)
    if not s:
        raise HTTPException(404)
    p = export.exporter_situation_latex(situations.projeter_situation(s), f"situation_{export.nom_fichier(s['titre'])[:40]}")
    if pdf:
        pp = export.compiler_pdf(p)
        if pp:
            return FileResponse(pp, filename=pp.name)
    return FileResponse(p, filename=p.name, media_type="application/x-tex")


class Validation(BaseModel):
    statut: str                      # valide | rejete | en_attente
    validateur: str = ""
    observations: Optional[str] = None
    motif_rejet: Optional[str] = None
    # champs corrigibles
    titre: Optional[str] = None
    tige: Optional[str] = None
    p1: Optional[str] = None; p2: Optional[str] = None; p3: Optional[str] = None; p4: Optional[str] = None; p5: Optional[str] = None
    reponse: Optional[int] = None
    correction_detaillee: Optional[str] = None
    erreurs_distracteurs: Optional[str] = None
    chapitre: Optional[str] = None
    difficulte: Optional[str] = None


@app.post("/api/items/{iid}/valider")
def valider(iid: str, v: Validation):
    if v.statut not in ("valide", "rejete", "en_attente"):
        raise HTTPException(400, "statut invalide")
    champs = {k: getattr(v, k) for k in ("titre", "tige", "p1", "p2", "p3", "p4", "p5", "reponse",
                                         "correction_detaillee", "erreurs_distracteurs", "chapitre", "difficulte")
              if getattr(v, k) is not None}
    with connect() as con:
        if not one(con, "SELECT id FROM items WHERE id=?", (iid,)):
            raise HTTPException(404)
        corrige = False
        for k, val in champs.items():
            cur = one(con, f"SELECT {k} v FROM items WHERE id=?", (iid,))["v"]
            if str(cur) != str(val):
                corrige = True
                con.execute(f"UPDATE items SET {k}=? WHERE id=?", (val, iid))
        if "tige" in champs:
            con.execute("UPDATE items SET nb_mots_tige=? WHERE id=?", (generation.compter_mots(champs["tige"]), iid))
        con.execute(
            "UPDATE items SET statut_validation=?, validateur=?, date_validation=?, observations=?, motif_rejet=?, "
            "version=CASE WHEN ? THEN 'corrigée' ELSE version END WHERE id=?",
            (v.statut, v.validateur, datetime.now().isoformat(timespec="minutes"), v.observations, v.motif_rejet,
             corrige, iid))
        return one(con, "SELECT * FROM items WHERE id=?", (iid,))


class Commande(BaseModel):
    jour: Optional[int] = None
    serie: Optional[str] = None
    discipline: Optional[str] = None
    sous_discipline: Optional[str] = None
    chapitre: Optional[str] = None
    difficulte: Optional[str] = None
    n: int = 5


@app.post("/api/generer")
def api_generer(c: Commande):
    try:
        if c.jour and not c.discipline:
            res = generation.generer_epreuve(c.jour, c.serie)
            return {"lots": [{"quota": r["quota"], "nb": len(r["ids"]), "usage": r["usage"]} for r in res]}
        if not c.discipline:
            raise HTTPException(400, "discipline ou jour requis")
        r = generation.generer(discipline=c.discipline, sous_discipline=c.sous_discipline, n=c.n,
                               chapitre=c.chapitre, difficulte=c.difficulte, jour=c.jour, serie=c.serie)
        return {"nb": len(r["ids"]), "usage": r["usage"], "anomalies_serie": r["anomalies_serie"]}
    except generation.GenerationError as e:
        raise HTTPException(400, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Erreur interne pendant la génération : {type(e).__name__} : {e}")


@app.get("/api/prompt")
def prompt_pour_copier(discipline: str, sous_discipline: Optional[str] = None, n: int = 5,
                       chapitre: Optional[str] = None, difficulte: Optional[str] = None):
    """Commande prête à coller dans Claude.ai si l'API n'est pas configurée."""
    with connect() as con:
        cmd = generation.composer_commande(con, discipline=discipline, sous_discipline=sous_discipline, n=n,
                                           chapitre=chapitre, difficulte=difficulte)
    return {"systeme": generation.PROMPT_SYSTEME, "commande": cmd}


class Import(BaseModel):
    items: list[dict]
    discipline: Optional[str] = None


@app.post("/api/importer")
def importer(imp: Import):
    """Importer un JSON produit dans Claude.ai (mode sans API)."""
    with connect() as con:
        for it in imp.items:
            it.setdefault("discipline", imp.discipline or "")
        ids = generation.inserer_items(con, imp.items, modele="import manuel")
    return {"nb": len(ids)}


# ------------------------------------------------------------------ assemblage (élève)

@app.get("/api/epreuve")
def api_epreuve(jour: int, option: str = "1.02", graine: Optional[int] = None):
    return assemblage.assembler_epreuve(jour, option, graine)


@app.get("/api/discipline")
def api_discipline(jour: int, discipline: str, option: str = "1.02", graine: Optional[int] = None):
    return assemblage.assembler_discipline(jour, discipline, option, graine)


@app.get("/api/chapitre")
def api_chapitre(discipline: str, chapitre: str, n: int = 10, difficulte: Optional[str] = None,
                 graine: Optional[int] = None):
    return assemblage.assembler_chapitre(discipline, chapitre, n, difficulte, graine)


@app.get("/api/banque.json")
def api_banque():
    """Banque validée + configuration : fichier embarqué par l'application élève (mode hors ligne)."""
    return assemblage.banque_validee()


@app.get("/api/export/latex")
def api_export_latex(jour: int, serie: str = "A", discipline: Optional[str] = None, pdf: bool = False):
    if discipline:
        s = assemblage.assembler_discipline(jour, discipline)
        nom, titre = f"J{jour}_{export.nom_fichier(discipline)}_serie{serie}", discipline
    else:
        s = assemblage.assembler_epreuve(jour)
        nom, titre = f"J{jour}_{s['epreuve']['code'].replace('.', '')}_serie{serie}", s["epreuve"]["libelle"]
    p = export.exporter_latex(s, nom, titre_epreuve=titre, code_epreuve=s["epreuve"]["code"], serie_lettre=serie,
                              duree=f"{s['epreuve']['duree_h']:g} h")
    if pdf:
        pp = export.compiler_pdf(p)
        if pp:
            return FileResponse(pp, filename=pp.name)
    return FileResponse(p, filename=p.name, media_type="application/x-tex")


class Resultat(BaseModel):
    eleve: Optional[str] = None
    mode: str
    option_code: Optional[str] = "1.02"
    jour: Optional[int] = None
    discipline: Optional[str] = None
    chapitre: Optional[str] = None
    nb_items: int
    score: int
    details: list[dict] = []
    date_passation: str


@app.post("/api/resultats")
def synchroniser_resultats(res: list[Resultat]):
    with connect() as con:
        for r in res:
            con.execute(
                "INSERT INTO resultats(eleve, mode, option_code, jour, discipline, chapitre, nb_items, score, details, date_passation) "
                "VALUES(?,?,?,?,?,?,?,?,?,?)",
                (r.eleve, r.mode, r.option_code, r.jour, r.discipline, r.chapitre, r.nb_items, r.score,
                 json.dumps(r.details, ensure_ascii=False), r.date_passation))
    return {"recus": len(res)}


# ------------------------------------------------------------------ statiques
app.mount("/validateur", StaticFiles(directory=STATIC / "validateur", html=True), name="validateur")
app.mount("/eleve", StaticFiles(directory=STATIC / "eleve", html=True), name="eleve")
