"""Comptes des enseignants : identifiants individuels, rôles, sessions signées.

- Mots de passe hachés (PBKDF2-SHA256, sel aléatoire).
- Session = jeton signé HMAC (identifiant + expiration) dans un cookie HttpOnly : aucun état serveur,
  donc plusieurs instances ou redémarrages ne déconnectent personne et les connexions parallèles sont libres.
- Rôles : admin (gère les comptes, produit, relit), redacteur (produit et relit), validateur (relit).
- Amorçage : au premier démarrage, si aucun compte n'existe et que ATELIER_MOT_DE_PASSE est défini,
  un compte administrateur « atelier » est créé avec ce mot de passe.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from .db import connect, maintenant, one, rows

ROLES = ("admin", "redacteur", "validateur")
DUREE_SESSION = 14 * 24 * 3600  # 14 jours


def _secret() -> bytes:
    s = os.environ.get("CLE_SECRETE") or os.environ.get("ATELIER_MOT_DE_PASSE") or "developpement-local"
    return hashlib.sha256(("exetat::" + s).encode()).digest()


# ------------------------------------------------------------------ mots de passe

def hacher(mdp: str) -> str:
    sel = secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac("sha256", mdp.encode(), sel, 200_000)
    return "pbkdf2$" + base64.b64encode(sel).decode() + "$" + base64.b64encode(h).decode()


def verifier_mdp(mdp: str, stocke: str) -> bool:
    try:
        _, sel, h = stocke.split("$")
        calc = hashlib.pbkdf2_hmac("sha256", mdp.encode(), base64.b64decode(sel), 200_000)
        return hmac.compare_digest(calc, base64.b64decode(h))
    except Exception:  # noqa: BLE001
        return False


# ------------------------------------------------------------------ jetons de session

def emettre_jeton(identifiant: str) -> str:
    corps = base64.urlsafe_b64encode(json.dumps({"u": identifiant, "exp": int(time.time()) + DUREE_SESSION}).encode()).decode().rstrip("=")
    sig = hmac.new(_secret(), corps.encode(), hashlib.sha256).hexdigest()[:32]
    return corps + "." + sig


def lire_jeton(jeton: str | None) -> str | None:
    if not jeton or "." not in jeton:
        return None
    corps, sig = jeton.rsplit(".", 1)
    if not hmac.compare_digest(hmac.new(_secret(), corps.encode(), hashlib.sha256).hexdigest()[:32], sig):
        return None
    try:
        data = json.loads(base64.urlsafe_b64decode(corps + "=" * (-len(corps) % 4)))
    except Exception:  # noqa: BLE001
        return None
    if data.get("exp", 0) < time.time():
        return None
    return data.get("u")


# ------------------------------------------------------------------ comptes

def creer_compte(con, identifiant: str, nom: str, mdp: str, role: str = "validateur", disciplines: str | None = None) -> dict:
    identifiant = identifiant.strip().lower()
    if not identifiant or len(mdp) < 6:
        raise ValueError("identifiant requis et mot de passe d'au moins 6 caractères")
    if role not in ROLES:
        raise ValueError("rôle invalide")
    if one(con, "SELECT 1 FROM utilisateurs WHERE identifiant=?", (identifiant,)):
        raise ValueError("cet identifiant existe déjà")
    con.execute("INSERT INTO utilisateurs(identifiant, nom, mdp_hash, role, disciplines, actif, cree_le) VALUES(?,?,?,?,?,1,?)",
                (identifiant, nom.strip() or identifiant, hacher(mdp), role, disciplines, maintenant()))
    return compte(con, identifiant)


def compte(con, identifiant: str) -> dict | None:
    c = one(con, "SELECT identifiant, nom, role, disciplines, actif, cree_le, derniere_connexion FROM utilisateurs WHERE identifiant=?", (identifiant,))
    return c


def authentifier(con, identifiant: str, mdp: str) -> dict | None:
    u = one(con, "SELECT * FROM utilisateurs WHERE identifiant=?", (identifiant.strip().lower(),))
    if not u or not u["actif"] or not verifier_mdp(mdp, u["mdp_hash"]):
        return None
    con.execute("UPDATE utilisateurs SET derniere_connexion=? WHERE identifiant=?", (maintenant(), u["identifiant"]))
    return compte(con, u["identifiant"])


def lister_comptes(con) -> list[dict]:
    return rows(con, "SELECT identifiant, nom, role, disciplines, actif, cree_le, derniere_connexion FROM utilisateurs ORDER BY nom")


def amorcer() -> None:
    """Crée l'administrateur initial à partir d'ATELIER_MOT_DE_PASSE si la table est vide."""
    mdp = os.environ.get("ATELIER_MOT_DE_PASSE", "")
    with connect() as con:
        if one(con, "SELECT 1 FROM utilisateurs LIMIT 1"):
            return
        if mdp:
            creer_compte(con, os.environ.get("ATELIER_UTILISATEUR", "atelier"), "Administrateur", mdp, "admin")
