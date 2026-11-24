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

from . import retours, assemblage, auth, export, generation, situations, taches
from .db import connect, one, preparer, rows
import os
import secrets
from fastapi import Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

app = FastAPI(title="Plateforme items EXETAT", version="0.2")

# ------------------------------------------------------------------ protection de l'atelier
# Chaque enseignant se connecte avec ses identifiants (cookie de session signé). Les écritures et les pages de
# l'atelier exigent une session ; l'espace élève et l'API de lecture restent libres.
PREFIXES_PROTEGES = ("/validateur", "/api/generer", "/api/importer", "/api/situations/generer", "/api/export/", "/api/taches",
                     "/api/comptes", "/api/qualite", "/docs", "/openapi.json")
PAGES_LIBRES = ("/validateur/connexion.html",)
from starlette.responses import RedirectResponse as _Redir, Response


def utilisateur_courant(request: Request) -> dict | None:
    ident = auth.lire_jeton(request.cookies.get("session"))
    if not ident:
        return None
    with connect() as con:
        u = auth.compte(con, ident)
    return u if u and u["actif"] else None


@app.middleware("http")
async def _proteger_atelier(request: Request, call_next):
    chemin = request.url.path
    protege = (chemin.startswith(PREFIXES_PROTEGES) and chemin not in PAGES_LIBRES) or chemin.endswith("/valider") or (
        chemin.startswith("/api/items") and request.method != "GET") or (
        chemin.startswith("/api/situations") and request.method != "GET" and not chemin.endswith("/generer"))
    if protege:
        u = utilisateur_courant(request)
        if not u:
            if chemin.startswith("/validateur"):
                return _Redir("/validateur/connexion.html", status_code=302)
            return Response('{"detail":"Connexion requise."}', status_code=401, media_type="application/json")
        request.state.utilisateur = u
    return await call_next(request)


class Connexion(BaseModel):
    identifiant: str
    mot_de_passe: str


@app.post("/api/connexion")
def api_connexion(c: Connexion):
    with connect() as con:
        u = auth.authentifier(con, c.identifiant, c.mot_de_passe)
    if not u:
        raise HTTPException(401, "Identifiant ou mot de passe incorrect.")
    from fastapi.responses import JSONResponse
    rep = JSONResponse(u)
    rep.set_cookie("session", auth.emettre_jeton(u["identifiant"]), httponly=True, samesite="lax", max_age=auth.DUREE_SESSION,
                   secure=os.environ.get("RENDER") is not None)
    return rep


@app.post("/api/deconnexion")
def api_deconnexion():
    from fastapi.responses import JSONResponse
    rep = JSONResponse({"ok": True})
    rep.delete_cookie("session")
    return rep


@app.get("/api/moi")
def api_moi(request: Request):
    u = utilisateur_courant(request)
    if not u:
        raise HTTPException(401, "Connexion requise.")
    return u


class CompteNouveau(BaseModel):
    identifiant: str
    nom: str
    mot_de_passe: str
    role: str = "validateur"
    disciplines: Optional[str] = None


class CompteMaj(BaseModel):
    nom: Optional[str] = None
    role: Optional[str] = None
    disciplines: Optional[str] = None
    actif: Optional[bool] = None
    mot_de_passe: Optional[str] = None


def _exiger_admin(request: Request):
    u = getattr(request.state, "utilisateur", None)
    if not u or u["role"] != "admin":
        raise HTTPException(403, "Réservé à l'administrateur.")
    return u


@app.get("/api/comptes")
def api_comptes(request: Request):
    _exiger_admin(request)
    with connect() as con:
        return auth.lister_comptes(con)


@app.post("/api/comptes")
def api_creer_compte(c: CompteNouveau, request: Request):
    _exiger_admin(request)
    try:
        with connect() as con:
            return auth.creer_compte(con, c.identifiant, c.nom, c.mot_de_passe, c.role, c.disciplines)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/comptes/{ident}")
def api_maj_compte(ident: str, c: CompteMaj, request: Request):
    admin = _exiger_admin(request)
    with connect() as con:
        if not auth.compte(con, ident):
            raise HTTPException(404)
        if c.nom is not None:
            con.execute("UPDATE utilisateurs SET nom=? WHERE identifiant=?", (c.nom, ident))
        if c.role is not None:
            if c.role not in auth.ROLES:
                raise HTTPException(400, "rôle invalide")
            con.execute("UPDATE utilisateurs SET role=? WHERE identifiant=?", (c.role, ident))
        if c.disciplines is not None:
            con.execute("UPDATE utilisateurs SET disciplines=? WHERE identifiant=?", (c.disciplines, ident))
        if c.actif is not None:
            if ident == admin["identifiant"] and not c.actif:
                raise HTTPException(400, "Vous ne pouvez pas désactiver votre propre compte.")
            con.execute("UPDATE utilisateurs SET actif=? WHERE identifiant=?", (1 if c.actif else 0, ident))
        if c.mot_de_passe:
            if len(c.mot_de_passe) < 6:
                raise HTTPException(400, "mot de passe trop court")
            con.execute("UPDATE utilisateurs SET mdp_hash=? WHERE identifiant=?", (auth.hacher(c.mot_de_passe), ident))
        return auth.compte(con, ident)


class MonMdp(BaseModel):
    ancien: str
    nouveau: str


@app.post("/api/moi/mot-de-passe")
def api_mon_mdp(c: MonMdp, request: Request):
    u = utilisateur_courant(request)
    if not u:
        raise HTTPException(401)
    with connect() as con:
        if not auth.authentifier(con, u["identifiant"], c.ancien):
            raise HTTPException(400, "Ancien mot de passe incorrect.")
        if len(c.nouveau) < 6:
            raise HTTPException(400, "Nouveau mot de passe trop court (6 caractères minimum).")
        con.execute("UPDATE utilisateurs SET mdp_hash=? WHERE identifiant=?", (auth.hacher(c.nouveau), u["identifiant"]))
    return {"ok": True}


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
            "options": rows(con, "SELECT * FROM options ORDER BY code"),
            "epreuves": rows(con, "SELECT * FROM epreuves ORDER BY code"),
            "quotas": rows(con, "SELECT * FROM quotas ORDER BY epreuve_code, ordre"),
            "option_epreuves": rows(con, "SELECT * FROM option_epreuves ORDER BY option_code, jour"),
            "programme": rows(con, "SELECT * FROM programme ORDER BY discipline, sous_discipline, id"),
        }


@app.get("/api/stats")
def stats():
    with connect() as con:
        return {
            "par_statut": rows(con, "SELECT statut_validation statut, COUNT(*) n FROM items WHERE situation_id IS NULL GROUP BY 1"),
            "par_epreuve": rows(con, "SELECT epreuve_code, discipline, COALESCE(sous_discipline,'') sous_discipline, statut_validation statut, COUNT(*) n FROM items WHERE situation_id IS NULL GROUP BY 1,2,3,4 ORDER BY 1,2,3,4"),
            "par_discipline": rows(con, "SELECT discipline, COALESCE(sous_discipline,'') sous_discipline, statut_validation statut, COUNT(*) n FROM items WHERE situation_id IS NULL GROUP BY 1,2,3 ORDER BY 1,2,3"),
            "situations": rows(con, "SELECT statut_validation statut, COUNT(*) n FROM situations GROUP BY 1"),
            "par_chapitre_valide": rows(con, "SELECT discipline, chapitre, difficulte, COUNT(*) n FROM items WHERE statut_validation='valide' GROUP BY 1,2,3 ORDER BY 1,2,3"),
            "lots": rows(con, "SELECT * FROM lots_generation ORDER BY id DESC LIMIT 20"),
            "resultats": rows(con, "SELECT mode, COUNT(*) n, ROUND(AVG(100.0*score/nb_items),1) pct FROM resultats GROUP BY 1"),
        }


# ------------------------------------------------------------------ items (atelier)

@app.get("/api/items")
def lister_items(statut: Optional[str] = None, discipline: Optional[str] = None, limite: int = 200,
                 situation: Optional[str] = None, epreuve: Optional[str] = None):
    sql, p = "SELECT * FROM items WHERE 1=1", []
    if epreuve:
        sql += " AND epreuve_code=?"; p.append(epreuve)
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
    epreuve_code: Optional[str] = None
    discipline: str
    sous_discipline: Optional[str] = None
    chapitre: Optional[str] = None
    n: int = 5


@app.post("/api/situations/generer")
def api_generer_situation(c: CommandeSituation):
    try:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise generation.GenerationError("ANTHROPIC_API_KEY manquante dans la configuration du serveur.")
        return {"tache": taches.lancer_situation(discipline=c.discipline, sous_discipline=c.sous_discipline,
                                                 chapitre=c.chapitre, n=max(3, min(7, c.n)), epreuve_code=c.epreuve_code)}
    except generation.GenerationError as e:
        raise HTTPException(400, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Erreur interne pendant la génération : {type(e).__name__} : {e}")


@app.get("/api/situations")
def api_lister_situations(statut: Optional[str] = None, discipline: Optional[str] = None, epreuve: Optional[str] = None):
    with connect() as con:
        return situations.lister_situations(con, statut, discipline, epreuve)


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
def api_valider_situation(sid: str, v: ValidationSituation, request: Request):
    u = getattr(request.state, "utilisateur", None)
    if u:
        v.validateur = u["nom"]
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
    attendu_statut: Optional[str] = None   # statut vu par le validateur ; refus si un collègue a statué entre-temps
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
def valider(iid: str, v: Validation, request: Request):
    if v.statut not in ("valide", "rejete", "en_attente"):
        raise HTTPException(400, "statut invalide")
    u = getattr(request.state, "utilisateur", None)
    if u:
        v.validateur = u["nom"]
    champs = {k: getattr(v, k) for k in ("titre", "tige", "p1", "p2", "p3", "p4", "p5", "reponse",
                                         "correction_detaillee", "erreurs_distracteurs", "chapitre", "difficulte")
              if getattr(v, k) is not None}
    with connect() as con:
        actuel = one(con, "SELECT statut_validation, validateur FROM items WHERE id=?", (iid,))
        if not actuel:
            raise HTTPException(404)
        if v.attendu_statut and actuel["statut_validation"] != v.attendu_statut and actuel["statut_validation"] != "en_attente":
            raise HTTPException(409, f"Cette question vient d'être traitée par {actuel['validateur'] or 'un collègue'} "
                                     f"({actuel['statut_validation']}). Rechargez-la avant de statuer.")
        avant = one(con, "SELECT * FROM items WHERE id=?", (iid,))
        corrige, diffs = False, []
        for k, val in champs.items():
            cur = avant[k]
            if str(cur) != str(val):
                corrige = True
                diffs.append((k, cur, val))
                con.execute(f"UPDATE items SET {k}=? WHERE id=?", (val, iid))
        retours.enregistrer(con, item_id=iid, type_="item", decision=v.statut, validateur=v.validateur or "anonyme",
                            motif=v.motif_rejet, observations=v.observations, meta=avant, diffs=diffs)
        if "tige" in champs:
            con.execute("UPDATE items SET nb_mots_tige=? WHERE id=?", (generation.compter_mots(champs["tige"]), iid))
        con.execute(
            "UPDATE items SET statut_validation=?, validateur=?, date_validation=?, observations=?, motif_rejet=?, "
            "version=CASE WHEN ? THEN 'corrigée' ELSE version END WHERE id=?",
            (v.statut, v.validateur, datetime.now().isoformat(timespec="minutes"), v.observations, v.motif_rejet,
             corrige, iid))
        return one(con, "SELECT * FROM items WHERE id=?", (iid,))


@app.get("/api/qualite")
def api_qualite(jours: int = 90):
    """Tableau de bord qualité : ce que les relectures disent de la production (admin et rédacteurs)."""
    with connect() as con:
        return retours.tableau(con, jours)


@app.get("/api/qualite/consignes")
def api_qualite_consignes(discipline: str, sous_discipline: Optional[str] = None):
    """Le bloc de retours tel qu'il sera joint à la prochaine commande dans cette matière."""
    with connect() as con:
        return {"discipline": discipline, "consignes": retours.consignes_pour(con, discipline, sous_discipline)}


class Commande(BaseModel):
    epreuve_code: Optional[str] = None
    jour: Optional[int] = None
    serie: Optional[str] = None
    discipline: Optional[str] = None
    sous_discipline: Optional[str] = None
    chapitre: Optional[str] = None
    difficulte: Optional[str] = None
    n: int = 5


@app.post("/api/generer")
def api_generer(c: Commande):
    """Lance la génération en arrière-plan et renvoie l'identifiant de la tâche (suivi : GET /api/taches/{id})."""
    try:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise generation.GenerationError("ANTHROPIC_API_KEY manquante dans la configuration du serveur.")
        if c.epreuve_code and not c.discipline:
            return {"tache": taches.lancer_epreuve(c.epreuve_code, c.serie)}
        if not c.discipline:
            raise HTTPException(400, "discipline ou épreuve requise")
        return {"tache": taches.lancer_items(discipline=c.discipline, sous_discipline=c.sous_discipline, n=c.n,
                                             chapitre=c.chapitre, difficulte=c.difficulte, serie=c.serie,
                                             epreuve_code=c.epreuve_code)}
    except generation.GenerationError as e:
        raise HTTPException(400, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Erreur interne pendant la génération : {type(e).__name__} : {e}")


@app.get("/api/taches")
def api_taches():
    return taches.liste()


@app.get("/api/taches/{tid}")
def api_tache(tid: str):
    t = taches.etat(tid)
    if not t:
        raise HTTPException(404)
    return t


@app.get("/api/prompt")
def prompt_pour_copier(discipline: str, sous_discipline: Optional[str] = None, n: int = 5,
                       chapitre: Optional[str] = None, difficulte: Optional[str] = None, epreuve: Optional[str] = None):
    """Commande prête à coller dans un assistant IA si l'API n'est pas configurée."""
    with connect() as con:
        cmd = generation.composer_commande(con, discipline=discipline, sous_discipline=sous_discipline, n=n,
                                           chapitre=chapitre, difficulte=difficulte, epreuve_code=epreuve)
    return {"systeme": generation.PROMPT_SYSTEME, "commande": cmd}


class Import(BaseModel):
    items: list[dict]
    discipline: Optional[str] = None
    epreuve_code: Optional[str] = None


@app.post("/api/importer")
def importer(imp: Import):
    """Importer un JSON produit avec un assistant IA (mode sans API)."""
    with connect() as con:
        for it in imp.items:
            it.setdefault("discipline", imp.discipline or "")
        ids = generation.inserer_items(con, imp.items, modele="import manuel", epreuve_code=imp.epreuve_code)
    return {"nb": len(ids)}


# ------------------------------------------------------------------ assemblage (élève)

@app.get("/api/epreuve")
def api_epreuve(code: str, graine: Optional[int] = None):
    return assemblage.assembler_epreuve(code, graine)


@app.get("/api/discipline")
def api_discipline(code: str, discipline: str, graine: Optional[int] = None):
    return assemblage.assembler_discipline(code, discipline, graine)


@app.get("/api/chapitre")
def api_chapitre(discipline: str, chapitre: str, n: int = 10, difficulte: Optional[str] = None,
                 graine: Optional[int] = None, code: Optional[str] = None):
    return assemblage.assembler_chapitre(discipline, chapitre, n, difficulte, graine, code)


@app.get("/api/banque.json")
def api_banque():
    """Banque validée + configuration : fichier embarqué par l'application élève (mode hors ligne)."""
    return assemblage.banque_validee()


@app.get("/api/export/latex")
def api_export_latex(code: str, serie: str = "A", discipline: Optional[str] = None, pdf: bool = False):
    if discipline:
        s = assemblage.assembler_discipline(code, discipline)
        nom, titre = f"{code.replace('.', '')}_{export.nom_fichier(discipline)}_serie{serie}", discipline
    else:
        s = assemblage.assembler_epreuve(code)
        nom, titre = f"{code.replace('.', '')}_serie{serie}", s["epreuve"]["libelle"]
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
    option_code: Optional[str] = None
    jour: Optional[int] = None
    epreuve_code: Optional[str] = None
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
                "INSERT INTO resultats(eleve, mode, option_code, jour, epreuve_code, discipline, chapitre, nb_items, score, details, date_passation) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (r.eleve, r.mode, r.option_code, r.jour, r.epreuve_code, r.discipline, r.chapitre, r.nb_items, r.score,
                 json.dumps(r.details, ensure_ascii=False), r.date_passation))
    return {"recus": len(res)}


# ------------------------------------------------------------------ statiques
app.mount("/validateur", StaticFiles(directory=STATIC / "validateur", html=True), name="validateur")
app.mount("/eleve", StaticFiles(directory=STATIC / "eleve", html=True), name="eleve")
