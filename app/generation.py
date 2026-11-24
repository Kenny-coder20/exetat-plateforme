"""Service de génération : construit la commande, appelle l'API Claude, vérifie, insère en attente."""
from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path

from dotenv import load_dotenv

from .db import connect, rows

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

PROMPT_SYSTEME = (ROOT / "docs" / "prompt_systeme.md").read_text(encoding="utf-8")
CHARTE = (ROOT / "docs" / "charte.md").read_text(encoding="utf-8")
CAHIER = (ROOT / "docs" / "cahier_des_charges.md").read_text(encoding="utf-8")

MODELE = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5")
DIFFICULTES = ("facile", "moyen", "difficile")


class GenerationError(Exception):
    pass


# ---------------------------------------------------------------- commandes

def repartition_difficulte(n: int) -> dict[str, int]:
    """25 / 50 / 25 arrondi : 15 -> 4/7/4 ; 20 -> 5/10/5 ; 6 -> 1/3/2 (ajusté)."""
    f = round(n * 0.25)
    d = round(n * 0.25)
    m = n - f - d
    if m < 0:
        m, d = 0, n - f
    return {"facile": f, "moyen": m, "difficile": d}


def repartir_chapitres(con, discipline: str, sous_discipline: str | None, n: int) -> list[str]:
    """Répartit n items sur les chapitres du programme au prorata des poids."""
    sql = "SELECT chapitre, poids FROM programme WHERE discipline=?"
    params: list = [discipline]
    if sous_discipline:
        sql += " AND sous_discipline=?"
        params.append(sous_discipline)
    chaps = rows(con, sql + " ORDER BY id", params)
    if not chaps:
        return ["(chapitre au choix dans le programme)"] * n
    total = sum(c["poids"] for c in chaps)
    quotas = [(c["chapitre"], c["poids"] / total * n) for c in chaps]
    attrib = {ch: int(q) for ch, q in quotas}
    reste = n - sum(attrib.values())
    for ch, q in sorted(quotas, key=lambda x: -(x[1] - int(x[1]))):
        if reste <= 0:
            break
        attrib[ch] += 1
        reste -= 1
    out: list[str] = []
    for ch, _ in quotas:
        out += [ch] * attrib[ch]
    return out


def composer_commande(con, *, discipline: str, sous_discipline: str | None, n: int,
                      chapitre: str | None = None, difficulte: str | None = None,
                      serie: str | None = None, jour: int | None = None) -> str:
    if chapitre:
        chapitres = [chapitre] * n
    else:
        chapitres = repartir_chapitres(con, discipline, sous_discipline, n)
    if difficulte:
        diffs = [difficulte] * n
    else:
        rep = repartition_difficulte(n)
        diffs = ["facile"] * rep["facile"] + ["moyen"] * rep["moyen"] + ["difficile"] * rep["difficile"]
        # entrelacer pour éviter trois difficiles consécutifs
        diffs = sorted(diffs, key=lambda d: DIFFICULTES.index(d))
        diffs = diffs[::2] + diffs[1::2]
    plan = "\n".join(f"- Item {i+1} : chapitre « {c} », difficulté {d}" for i, (c, d) in enumerate(zip(chapitres, diffs)))
    sd = f" (sous-discipline : {sous_discipline})" if sous_discipline else ""
    s = f", série {serie}" if serie else ""
    j = f", jour {jour}" if jour else ""
    return (
        f"COMMANDE : génère {n} items de {discipline}{sd}{j}{s}, option 1.02 Sciences, selon le plan suivant.\n"
        f"{plan}\n"
        "Respecte le plan item par item (chapitre et difficulté). Varie les familles de contexte et la position "
        "de la bonne réponse. Réponds uniquement par le JSON demandé."
    )


# ---------------------------------------------------------------- appel API

def appeler_claude(commande: str, max_tokens: int = 16000) -> tuple[dict, dict]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise GenerationError("ANTHROPIC_API_KEY manquante : copiez .env.example vers .env et renseignez la clé.")
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    system = [
        {"type": "text", "text": PROMPT_SYSTEME},
        {"type": "text", "text": "=== CHARTE DE RÉDACTION ===\n" + CHARTE, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": "=== CAHIER DES CHARGES ===\n" + CAHIER, "cache_control": {"type": "ephemeral"}},
    ]
    msg = client.messages.create(
        model=MODELE,
        max_tokens=max_tokens,
        temperature=0.4,
        system=system,
        messages=[{"role": "user", "content": commande}],
    )
    texte = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    usage = {"in": msg.usage.input_tokens, "out": msg.usage.output_tokens}
    return parser_json(texte), usage


def parser_json(texte: str) -> dict:
    texte = texte.strip()
    texte = re.sub(r"^```(?:json)?\s*|\s*```$", "", texte)
    debut, fin = texte.find("{"), texte.rfind("}")
    if debut < 0 or fin < 0:
        raise GenerationError("Réponse sans JSON : " + texte[:200])
    try:
        return json.loads(texte[debut:fin + 1])
    except json.JSONDecodeError as e:
        raise GenerationError(f"JSON invalide ({e}) : {texte[:200]}")


# ---------------------------------------------------------------- vérification

def compter_mots(s: str) -> int:
    return len(re.findall(r"\S+", s))


def verifier_item(it: dict) -> list[str]:
    """Contrôles mécaniques de la charte. Retourne la liste des anomalies (vide = OK)."""
    pb = []
    props = it.get("propositions") or []
    if len(props) != 5:
        pb.append("5 propositions attendues")
    if len({p.strip().lower() for p in props}) != len(props):
        pb.append("propositions en double")
    r = it.get("reponse")
    if not isinstance(r, int) or not 1 <= r <= 5:
        pb.append("réponse hors 1..5")
    nb = compter_mots(it.get("tige", ""))
    it["nb_mots_tige"] = nb
    if nb < 30:
        pb.append(f"tige trop courte ({nb} mots)")
    if nb > 95:
        pb.append(f"tige trop longue ({nb} mots)")
    if it.get("difficulte") not in DIFFICULTES:
        pb.append("difficulté invalide")
    if "?" not in it.get("tige", ""):
        pb.append("pas de question directe")
    if any("aucune des" in p.lower() for p in props):
        pb.append("« aucune des réponses » interdit")
    for champ in ("titre", "tige", "savoir_essentiel", "correction_detaillee"):
        if not it.get(champ):
            pb.append(f"champ manquant : {champ}")
    return pb


def verifier_serie(items: list[dict]) -> list[str]:
    pb = []
    if not items:
        return ["aucun item"]
    from collections import Counter

    c = Counter(it.get("reponse") for it in items)
    for k, v in c.items():
        if v / len(items) > 0.34 and len(items) >= 6:
            pb.append(f"réponse {k} trop fréquente ({v}/{len(items)})")
    return pb


# ---------------------------------------------------------------- insertion

def inserer_items(con, items: list[dict], *, option_code="1.02", jour=None, epreuve_code=None,
                  serie=None, numero_depart=1, modele=MODELE) -> list[str]:
    ids = []
    for k, it in enumerate(items):
        anomalies = verifier_item(it)
        obs = it.get("observations") or ""
        if anomalies:
            obs = ("ANOMALIES AUTO : " + " ; ".join(anomalies) + ". " + obs).strip()
        iid = f"GEN-{uuid.uuid4().hex[:10]}"
        p = it["propositions"] + [""] * (5 - len(it["propositions"]))
        con.execute(
            """INSERT INTO items(id, option_code, jour, epreuve_code, serie, numero, discipline, sous_discipline,
               chapitre, savoir_essentiel, competence, difficulte, famille_contexte, support, support_latex, titre, tige,
               p1,p2,p3,p4,p5, reponse, correction_detaillee, erreurs_distracteurs, nb_mots_tige, modele, observations)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (iid, option_code, jour, epreuve_code, serie, numero_depart + k, it["discipline"],
             it.get("sous_discipline") or None, it.get("chapitre"), it["savoir_essentiel"], it.get("competence"),
             it.get("difficulte", "moyen"), it.get("famille_contexte"), it.get("support") or "aucun",
             it.get("support_latex"), it["titre"], it["tige"], p[0], p[1], p[2], p[3], p[4],
             int(it.get("reponse") or 1), it["correction_detaillee"], it.get("erreurs_distracteurs"),
             it.get("nb_mots_tige"), modele, obs or None),
        )
        ids.append(iid)
    return ids


# ---------------------------------------------------------------- points d'entrée

def generer(*, discipline: str, sous_discipline: str | None = None, n: int = 5, chapitre: str | None = None,
            difficulte: str | None = None, jour: int | None = None, serie: str | None = None,
            epreuve_code: str | None = None, numero_depart: int = 1) -> dict:
    """Génère n items d'une discipline et les enregistre en attente de validation."""
    with connect() as con:
        commande = composer_commande(con, discipline=discipline, sous_discipline=sous_discipline, n=n,
                                     chapitre=chapitre, difficulte=difficulte, serie=serie, jour=jour)
        lot = con.execute("INSERT INTO lots_generation(commande, modele, nb_demandes) VALUES(?,?,?)",
                          (commande, MODELE, n)).lastrowid
        try:
            data, usage = appeler_claude(commande)
        except Exception as e:  # noqa: BLE001
            con.execute("UPDATE lots_generation SET erreur=? WHERE id=?", (str(e), lot))
            raise
        items = data.get("items", [])
        for it in items:
            it.setdefault("discipline", discipline)
            if sous_discipline and not it.get("sous_discipline"):
                it["sous_discipline"] = sous_discipline
        ids = inserer_items(con, items, jour=jour, epreuve_code=epreuve_code, serie=serie,
                            numero_depart=numero_depart)
        con.execute("UPDATE lots_generation SET nb_recus=?, cout_tokens_in=?, cout_tokens_out=? WHERE id=?",
                    (len(ids), usage["in"], usage["out"], lot))
        return {"lot": lot, "ids": ids, "usage": usage, "anomalies_serie": verifier_serie(items)}


def generer_epreuve(jour: int, serie: str | None = None, option_code: str = "1.02") -> list[dict]:
    """Génère une épreuve complète du jour, quota par quota (un appel API par quota)."""
    with connect() as con:
        ep = con.execute("SELECT * FROM epreuves WHERE option_code=? AND jour=?", (option_code, jour)).fetchone()
        if not ep:
            raise GenerationError(f"Pas d'épreuve pour l'option {option_code}, jour {jour}")
        if not ep["actif"]:
            raise GenerationError(f"L'épreuve {ep['code']} (jour {jour}) est hors périmètre pour l'instant.")
        quotas = rows(con, "SELECT * FROM quotas WHERE epreuve_id=? ORDER BY ordre", (ep["id"],))
    resultats = []
    numero = 1
    for q in quotas:
        r = generer(discipline=q["discipline"], sous_discipline=q["sous_discipline"], n=q["nb_items"],
                    jour=jour, serie=serie, epreuve_code=ep["code"], numero_depart=numero)
        numero += q["nb_items"]
        resultats.append({"quota": q, **r})
    return resultats
