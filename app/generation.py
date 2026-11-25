"""Service de génération : construit la commande, appelle le modèle IA, vérifie, insère en attente."""
from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path

from dotenv import load_dotenv

from .contextes import CONSIGNE_VARIETE, decrire, plan_contextes
from .db import connect, rows
from .retours import consignes_pour

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

PROMPT_SYSTEME = (ROOT / "docs" / "prompt_systeme.md").read_text(encoding="utf-8")
CHARTE = (ROOT / "docs" / "charte.md").read_text(encoding="utf-8")
CAHIER = (ROOT / "docs" / "cahier_des_charges.md").read_text(encoding="utf-8")

MODELE = os.environ.get("MODELE_IA") or os.environ.get("CLAUDE_MODEL") or "claude-sonnet-5-5"
# si le modèle configuré n'existe pas pour la clé, on essaie ces identifiants dans l'ordre
MODELES_SECOURS = [m for m in ("claude-sonnet-5-5", "claude-sonnet-4-5", "claude-opus-5-5") if m != MODELE]
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


# Part d'items « décision » (QCM situationnel à calcul justificatif implicite) selon la discipline, en mode mélange
PART_DECISION = {"Mathématiques": 0.4, "Physique": 0.5, "Chimie": 0.5, "SVT": 0.35, "Géographie": 0.35, "TIC": 0.35,
                 "Civisme": 0.25, "Histoire": 0.15, "Philosophie": 0.2, "Actualité": 0.0, "Questions d'actualité": 0.0}
PART_DECISION_DEFAUT = 0.4  # disciplines techniques et commerciales


def plan_types(discipline: str, n: int, type_item: str | None) -> list[str]:
    """Attribue à chaque item son type : « classique » ou « decision », répartis sur la série."""
    if type_item in ("classique", "decision"):
        return [type_item] * n
    part = PART_DECISION.get(discipline, PART_DECISION_DEFAUT)
    k = round(n * part)
    if n >= 2 and part > 0:
        k = max(1, k)
    types = ["classique"] * n
    if k:
        pas = n / k
        for i in range(k):
            types[min(n - 1, int(i * pas + pas / 2))] = "decision"
    return types


DISCIPLINES_ACTUALITE = {"Actualité", "Questions d'actualité"}


def est_actualite(discipline: str | None) -> bool:
    return (discipline or "") in DISCIPLINES_ACTUALITE


def fenetre_actualite() -> tuple[str, str]:
    """Période de référence fixée par le jury (ACTUALITE_DEBUT / ACTUALITE_FIN, AAAA-MM-JJ) ;
    par défaut du 1er janvier de l'année précédente à aujourd'hui."""
    import datetime as _dt
    auj = _dt.date.today()
    debut = os.environ.get("ACTUALITE_DEBUT") or f"{auj.year - 1}-01-01"
    fin = os.environ.get("ACTUALITE_FIN") or auj.isoformat()
    return debut, fin


def consigne_actualite() -> str:
    debut, fin = fenetre_actualite()
    return (
        "=== MATIÈRE ACTUALITÉ — RÈGLES PARTICULIÈRES ===\n"
        f"- Fenêtre temporelle fixée par le jury : du {debut} au {fin}. Chaque item porte sur un fait survenu dans cette fenêtre ; "
        "aucun fait postérieur, aucun fait antérieur sauf pour situer un contexte.\n"
        "- Tu disposes d'un outil de recherche web : UTILISE-LE avant de rédiger, pour chaque item, afin de vérifier le fait, la date, "
        "les noms et les chiffres auprès d'une source fiable (institution, agence de presse, organisation internationale, média de référence). "
        "N'écris jamais un item de mémoire.\n"
        "- Faits vérifiables et stabilisés uniquement : nominations, résultats officiels, dates, décisions, textes promulgués, chiffres officiels. "
        "Pas de pronostic, pas d'opinion, pas de fait divers, pas de rumeur.\n"
        "- Neutralité : les items de vie politique portent sur des faits institutionnels (qui occupe quelle fonction, quel texte a été adopté, "
        "quelle décision a été prise), jamais sur des jugements de valeur ni sur des personnes privées.\n"
        "- La correction détaillée cite la source (institution ou média et date) pour permettre la relecture par les enseignants.\n"
        "- Compétences visées : identifier (qui, quoi, où, quand), situer (chronologie, géographie), relier (cause, conséquence, rôle d'une institution).\n"
        "- Le contexte imposé du plan n'est qu'une amorce d'une ou deux phrases ; les noms, lieux et dates réels de l'événement priment toujours sur lui.\n"
        "- Les distracteurs sont des confusions plausibles (pays voisin, institution voisine, année voisine, fonction voisine), jamais des inventions absurdes."
    )


def composer_commande(con, *, discipline: str, sous_discipline: str | None, n: int,
                      chapitre: str | None = None, difficulte: str | None = None,
                      serie: str | None = None, jour: int | None = None, epreuve_code: str | None = None,
                      type_item: str | None = None) -> str:
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
    ctx = plan_contextes(n)
    types = plan_types(discipline, n, type_item)
    libelle_type = {"classique": "classique", "decision": "DÉCISION (QCM situationnel à calcul justificatif implicite : aucune consigne de calcul dans l'énoncé ; 5 propositions « décision + car + justification chiffrée »)"}
    plan = "\n".join(
        f"- Item {i+1} : chapitre « {c} », difficulté {d}, type {libelle_type[t]}\n    contexte imposé → {decrire(ctx[i])}"
        for i, (c, d, t) in enumerate(zip(chapitres, diffs, types))
    )
    sd = f" (sous-discipline : {sous_discipline})" if sous_discipline else ""
    s = f", série {serie}" if serie else ""
    j = f", épreuve {epreuve_code}" if epreuve_code else ""
    retours_txt = consignes_pour(con, discipline, sous_discipline, epreuve_code)
    actu_txt = consigne_actualite() if est_actualite(discipline) else ""
    return (
        f"COMMANDE : génère {n} items de {discipline}{sd}{j}{s} (Examen d'État, E.32), selon le plan suivant.\n"
        f"{plan}\n\n"
        f"{CONSIGNE_VARIETE}\n"
        + (actu_txt + "\n" if actu_txt else "")
        + (retours_txt + "\n" if retours_txt else "")
        + "Respecte le plan item par item (chapitre, difficulté, contexte imposé). Varie la position "
        "de la bonne réponse. Réponds uniquement par le JSON demandé."
    )


# ---------------------------------------------------------------- appel API

def appeler_modele(commande: str, max_tokens: int = 16000, recherche_web: bool = False) -> tuple[dict, dict]:
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
    msg = None
    essais = [MODELE] + MODELES_SECOURS
    for k, modele in enumerate(essais):
        try:
            params = dict(model=modele, max_tokens=max_tokens, system=system,
                          messages=[{"role": "user", "content": commande}])
            if recherche_web:  # outil de recherche web côté serveur Anthropic (matière Actualité)
                params["tools"] = [{"type": "web_search_20250305", "name": "web_search", "max_uses": int(os.environ.get("ACTUALITE_RECHERCHES_MAX", "10"))}]
            msg = client.messages.create(**params)
            break
        except anthropic.NotFoundError as e:
            if k == len(essais) - 1:
                raise GenerationError(f"Aucun modèle utilisable pour cette clé API (essayés : {', '.join(essais)}). "
                                      f"Renseignez MODELE_IA avec un identifiant valide. ({e})")
        except anthropic.AuthenticationError:
            raise GenerationError("Clé API Anthropic refusée : vérifiez ANTHROPIC_API_KEY.")
        except anthropic.APIStatusError as e:
            raise GenerationError(f"Erreur de l'API Anthropic ({e.status_code}) : {e.message}")
    texte = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    usage = {"in": msg.usage.input_tokens, "out": msg.usage.output_tokens}
    recherches = getattr(getattr(msg.usage, "server_tool_use", None), "web_search_requests", 0) or 0
    if recherches:
        usage["recherches_web"] = recherches
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
    if it.get("type_item") == "decision":
        tige = (it.get("tige") or "").lower()
        if re.search(r"\b(calcul\w*|détermin\w*|combien|quelle est la valeur|quelle valeur)\b", tige):
            pb.append("type décision : consigne de calcul explicite dans l'énoncé")
        just = sum(1 for p in props if re.search(r"\bcar\b|parce qu|puisque|\bdonc\b", p.lower()))
        if just < 4:
            pb.append(f"type décision : propositions sans justification ({just}/5 avec « car »)")
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

def inserer_items(con, items: list[dict], *, option_code=None, jour=None, epreuve_code=None,
                  serie=None, numero_depart=1, modele=MODELE) -> list[str]:
    ids = []
    for k, it in enumerate(items):
        anomalies = verifier_item(it)
        obs = it.get("observations") or ""
        if anomalies:
            obs = ("ANOMALIES AUTO : " + " ; ".join(anomalies) + ". " + obs).strip()
        iid = it.get("id") or f"GEN-{uuid.uuid4().hex[:10]}"
        p = it["propositions"] + [""] * (5 - len(it["propositions"]))
        support = it.get("support") or ("figure" if it.get("figure_svg") else "aucun")
        type_item = it.get("type_item") if it.get("type_item") in ("classique", "decision") else "classique"
        con.execute(
            """INSERT INTO items(id, option_code, jour, epreuve_code, serie, numero, discipline, sous_discipline,
               chapitre, savoir_essentiel, competence, difficulte, famille_contexte, support, support_latex, figure_svg, figure_legende,
               type_item, titre, tige, p1,p2,p3,p4,p5, reponse, correction_detaillee, erreurs_distracteurs, nb_mots_tige, modele, observations)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (iid, option_code, jour, it.get("epreuve_code") or epreuve_code, serie, numero_depart + k, it["discipline"],
             it.get("sous_discipline") or None, it.get("chapitre"), it["savoir_essentiel"], it.get("competence"),
             it.get("difficulte", "moyen"), it.get("famille_contexte"), support,
             it.get("support_latex"), it.get("figure_svg"), it.get("figure_legende"), type_item, it["titre"], it["tige"], p[0], p[1], p[2], p[3], p[4],
             int(it.get("reponse") or 1), it["correction_detaillee"], it.get("erreurs_distracteurs"),
             it.get("nb_mots_tige"), modele, obs or None),
        )
        ids.append(iid)
    return ids


# ---------------------------------------------------------------- points d'entrée

def generer(*, discipline: str, sous_discipline: str | None = None, n: int = 5, chapitre: str | None = None,
            difficulte: str | None = None, jour: int | None = None, serie: str | None = None,
            epreuve_code: str | None = None, numero_depart: int = 1, type_item: str | None = None) -> dict:
    """Génère n items d'une discipline et les enregistre en attente de validation."""
    with connect() as con:
        commande = composer_commande(con, discipline=discipline, sous_discipline=sous_discipline, n=n,
                                     chapitre=chapitre, difficulte=difficulte, serie=serie, epreuve_code=epreuve_code, type_item=type_item)
        lot = con.execute("INSERT INTO lots_generation(commande, modele, nb_demandes) VALUES(?,?,?)",
                          (commande, MODELE, n)).lastrowid
        try:
            data, usage = appeler_modele(commande, recherche_web=est_actualite(discipline))
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


def epreuve_et_quotas(con, epreuve_code: str):
    ep = con.execute("SELECT * FROM epreuves WHERE code=?", (epreuve_code,)).fetchone()
    if not ep:
        raise GenerationError(f"Épreuve {epreuve_code} inconnue dans le E.32 chargé.")
    quotas = rows(con, "SELECT * FROM quotas WHERE epreuve_code=? ORDER BY ordre", (epreuve_code,))
    return dict(ep), quotas


def generer_epreuve(epreuve_code: str, serie: str | None = None) -> list[dict]:
    """Génère une épreuve complète (code M.xx), quota par quota (un appel API par quota)."""
    with connect() as con:
        ep, quotas = epreuve_et_quotas(con, epreuve_code)
        if not ep["actif"]:
            raise GenerationError(f"L'épreuve {epreuve_code} n'est pas encore ouverte dans la plateforme.")
    resultats = []
    numero = 1
    for q in quotas:
        r = generer(discipline=q["discipline"], sous_discipline=q["sous_discipline"], n=q["nb_items"],
                    serie=serie, epreuve_code=epreuve_code, numero_depart=numero)
        numero += q["nb_items"]
        resultats.append({"quota": q, **r})
    return resultats
