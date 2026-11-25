"""Complément de programmes à partir des sommaires de manuels de 4e année (manuels-scolaires-rdc.com).

Source secondaire : manuels présentés comme conformes au programme officiel de l'EPST. Chaque ligne est marquée
« manuel — à confirmer » pour que l'inspecteur la valide. Seules les disciplines du E.32 encore sans programme sont
alimentées. Entrée : docs/programmes/sources/programmes_4e_manuels_rdc.json ; sortie : docs/programmes/complement_manuels.json.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
from app import e32  # noqa: E402

SRC = json.load(open(RACINE / "docs/programmes/sources/programmes_4e_manuels_rdc.json", encoding="utf-8"))["cours"]

# (discipline E.32) -> liste de (option du site, intitulé du cours) par ordre de préférence
CORRESPONDANCE: dict[str, list[tuple[str, str]]] = {
    "Organisation des entreprises": [("Commerciale et gestion", "Organisation des entreprises"), ("Secrétariat-administration", "Organisation des entreprises")],
    "Entrepreneuriat": [("Agriculture générale", "Entrepreneuriat"), ("Secrétariat-administration", "Entrepreneuriat")],
    "Mécanique appliquée": [("Mécanique générale", "Mécanique appliquée")],
    "Mécanique": [("Mécanique générale", "Mécanique appliquée")],
    "Législation sociale": [("Sociale", "Législation sociale")],
    "Législation sociale et organisation du tourisme": [("Sociale", "Législation sociale")],
    "Législation fiscale et sociale": [("Sociale", "Législation sociale"), ("Commerciale et gestion", "Fiscalité")],
    "Électricité": [("Mécanique générale", "Électricité générale"), ("Électricité", "Électricité générale")],
    "Électricité générale": [("Électricité", "Électricité générale")],
    "Électricité industrielle": [("Électronique", "Électricité industrielle")],
    "Électricité automobile": [("Mécanique automobile", "Électricité automobile")],
    "Développement rural": [("Agriculture générale", "Développement rural")],
    "Résistance des matériaux": [("Construction", "Résistance des matériaux"), ("Mécanique générale", "Résistance des matériaux")],
    "Résistance des matériaux et éléments des machines": [("Mécanique automobile", "Résistance des matériaux"), ("Mécanique automobile", "Éléments des machines")],
    "Électronique": [("Électronique", "Électronique générale")],
    "Automation": [("Mécanique automobile", "Automation")],
    "Régulation": [("Électronique", "Régulation")],
    "Esthétique": [("Pédagogie générale", "Esthétique")],
    "Législation": [("Construction", "Législation de la construction")],
    "Microbiologie": [("Sciences", "Microbiologie")],
    "Métallurgie": [("Mines et géologie", "Métallurgie extractive")],
    "Éléments de génie métallurgique": [("Mines et géologie", "Métallurgie extractive")],
    "Physique industrielle": [("Pétrochimie", "Physique industrielle")],
    "Béton armé": [("Construction", "Béton armé")],
    "Construction": [("Mécanique automobile", "Construction")],
    "Construction mécanique": [("Mécanique générale", "Construction mécanique")],
    "Diététique": [("Nutrition", "Diététique et nutrition"), ("Nutrition", "Diététique")],
    "Géographie touristique": [("Hôtellerie et restauration", "Géographie touristique")],
    "Hygiène et sécurité du travail": [("Sociale", "Hygiène et sécurité du travail")],
    "Hygiène": [("Sociale", "Hygiène et sécurité du travail")],
    "Latin": [("Latin-philosophie", "Latin")],
    "Organisation du bureau": [("Secrétariat-administration", "Organisation de bureau")],
    "Procédés généraux de construction": [("Construction", "Procédés généraux de construction")],
    "Psychologie sociale": [("Hôtesse d’accueil", "Psychologie sociale")],
    "Radiotélévision": [("Électronique", "Radio et TV")],
    "Technologie culinaire": [("Nutrition", "Technologie culinaire et nutrition")],
    "Technologie du restaurant": [("Hôtellerie et restauration", "Technologie de restaurant")],
    "Technologie hôtelière": [("Hôtellerie et restauration", "Technologie hôtelière et économat")],
    "Zootechnie": [("Vétérinaire", "Zootechnie")],
    "Économie du développement": [("Commerciale et gestion", "Économie et développement")],
    "Agriculture": [("Agriculture générale", "Agriculture générale")],
    "Agrostologie": [("Agriculture générale", "Agrostologie")],
    "Amélioration des plantes cultivées": [("Agriculture générale", "Amélioration des plantes")],
    "Aménagement forestier": [("Agriculture générale", "Aménagement forestier durable")],
    "Chirurgie": [("Vétérinaire", "Chirurgie")],
    "Cultures fourragères": [("Vétérinaire", "Cultures fourragères")],
    "Démographie": [("Sociale", "Démographie")],
    "Déontologie": [("Sociale", "Déontologie professionnelle")],
    "Déontologie professionnelle": [("Commerciale et gestion", "Déontologie professionnelle")],
    "Doctrines sociales": [("Sociale", "Doctrine sociale")],
    "Exploitation forestière": [("Foresterie", "Exploitation forestière")],
    "Finances publiques": [("Commerciale et gestion", "Finances publiques")],
    "Finances publiques et droit fiscal": [("Commerciale et gestion", "Finances publiques"), ("Commerciale et gestion", "Fiscalité")],
    "Fiscalité": [("Commerciale et gestion", "Fiscalité")],
    "Génie rural": [("Agriculture générale", "Génie rural")],
    "Histoire du travail et organisation professionnelle": [("Sociale", "Histoire du travail")],
    "Industries du bois": [("Foresterie", "Technologie du bois")],
    "Maladies infectieuses": [("Vétérinaire", "Maladies infectieuses du gros bétail")],
    "Maladies parasitaires": [("Vétérinaire", "Maladies parasitaires du gros bétail")],
    "Moteurs thermiques": [("Mécanique automobile", "Moteurs thermiques")],
    "Obstétrique": [("Vétérinaire", "Obstétrique vétérinaire")],
    "Organisation du travail": [("Sociale", "Organisation et la gestion du travail")],
    "Outillage de chantier": [("Construction", "Outillage de chantier")],
    "Pathologie": [("Vétérinaire", "Pathologie")],
    "Pharmacologie": [("Vétérinaire", "Pharmacologie")],
    "Phytopathologie": [("Agriculture générale", "Phytopathologie")],
    "Protection de l'enfance": [("Sociale", "Protection de l'enfant")],
    "Psychologie appliquée": [("Sociale", "Psychologie appliquée")],
    "Pétrochimie": [("Pétrochimie", "Pétrochimie")],
    "Technologie du pétrole": [("Pétrochimie", "Raffinage"), ("Pétrochimie", "Pétrochimie")],
    "Sécurité pétrolière": [("Pétrochimie", "Sécurité industrielle")],
    "Sécurité industrielle": [("Pétrochimie", "Sécurité industrielle"), ("Mines et géologie", "Sécurité")],
    "Santé et sécurité du travail": [("Mines et géologie", "Sécurité")],
    "Secourisme": [("Hôtesse d’accueil", "Secourisme")],
    "Statistique": [("Secrétariat-administration", "Statistiques")],
    "Technologie agricole": [("Agriculture générale", "Technologie agricole")],
    "Technologie de la spécialité": [("Coupe et couture", "Technologie de la spécialité")],
    "Technologie des textiles": [("Coupe et couture", "Technologie des textiles")],
    "Topographie": [("Construction", "Topographie")],
    "Voies de communication": [("Construction", "Voies de communication")],
    "Économie financière": [("Hôtesse d’accueil", "Économie financière")],
    "Œnologie et boissons": [("Hôtellerie et restauration", "Œnologie et boissons")],
    "Télécommunication": [("Électronique", "Télécommunication")],
    "Géologie": [("Mines et géologie", "Géologie de la RDC"), ("Pétrochimie", "Géologie et pétrochimie")],
    "Géologie générale": [("Pétrochimie", "Géologie et pétrochimie")],
    "Correspondance commerciale française": [("Secrétariat-administration", "Correspondance commerciale française")],
    "Comptabilité analytique de gestion": [("Commerciale et gestion", "Comptabilité analytique")],
    "Comptabilité": [("Commerciale et gestion", "Comptabilité générale")],
    "Exploitation des mines à ciel ouvert": [("Mines et géologie", "Exploitation des mines III")],
    "Exploitation des mines souterraines": [("Mines et géologie", "Exploitation des mines III")],
    "Levés géologiques": [("Mines et géologie", "Prospection et recherche minière")],
    "Levés géochimiques": [("Mines et géologie", "Prospection et recherche minière")],
    "Levés géophysiques": [("Mines et géologie", "Prospection et recherche minière")],
    "Technologie machines": [("Menuiserie-ébénisterie", "Technologie professionnelle")],
    "Technologie meubles": [("Menuiserie-ébénisterie", "Fabrication de meubles")],
    "Menuiserie de bâtiment": [("Menuiserie-ébénisterie", "Menuiserie")],
    "Biologie (anatomie, physiologie)": [("Nutrition", "Anatomie")],
    "Anatomie et physiologie": [("Nutrition", "Anatomie")],
    "Éducation à la citoyenneté": [],  # alias de Civisme, traité dans le seed
    "Technologie": [("Agriculture générale", "Technologie agricole")],
    "Environnement": [("Plomberie", "Environnement")],
    "Chimie appliquée": [("Mécanique générale", "Chimie")],
    "Physique appliquée": [("Mécanique générale", "Physique")],
    "Calcul professionnel": [("Plomberie", "Calculs professionnels")],
    "Technologie de soudure": [("Mécanique générale", "Technologie mécanique")],
    "Organes de transmission": [("Mécanique générale", "Mécanismes")],
    "Conservation des produits agricoles": [("Industries agricoles", "Technologie des boissons et des fermentations"), ("Agriculture générale", "Technologie agricole")],
    "Contrôle de fabrication": [("Industries agricoles", "Assurance qualité et HACCP")],
    "Génie industriel": [("Industries agricoles", "Gestion d'une unité agro-industrielle")],
    "Économie alimentaire": [("Industries agricoles", "Législation alimentaire et commercialisation")],
    "Hygiène alimentaire et nutrition": [("Industries agricoles", "Formulation et nutrition appliquée")],
    "Enquête nutritionnelle": [("Nutrition", "Diététique et nutrition")],
    "Gestion et administration": [("Industries agricoles", "Gestion d'une unité agro-industrielle")],
    "Biologie appliquée": [("Hôtellerie et restauration", "Microbiologie")],
    "Technique de laboratoire et chimie": [("Mécanique générale", "Chimie")],
    "Dendrologie": [("Foresterie", "Gestion forestière communautaire")],
    "Sylviculture": [("Foresterie", "Gestion forestière communautaire")],
    "Législation forestière": [("Foresterie", "Gestion forestière communautaire")],
    "Comptabilité hôtelière": [("Commerciale et gestion", "Comptabilité générale")],
    "Direction des travaux": [("Construction", "Organisation et gestion de chantier")],
    "Technologie générale": [("Mécanique générale", "Technologie mécanique")],
    "Histoire de l'art": [("Pédagogie générale", "Esthétique")],
    "Tourisme": [("Hôtellerie et restauration", "Géographie touristique")],
    "Économie générale": [("Commerciale et gestion", "Économie et développement")],
    "Économie de l'entreprise": [("Commerciale et gestion", "Organisation des entreprises")],
    "Sociologie et animation des loisirs": [("Sociale", "Développement communautaire")],
    "Conservation des ressources naturelles": [("Agriculture générale", "Aménagement forestier durable")],
    "Biologie animale": [("Vétérinaire", "Zootechnie")],
    "Circuits logiques": [("Électronique", "Électronique industrielle")],
    "Informatique et microprocesseur": [("Électronique", "Électronique industrielle")],
    "Instruments et équipements de diagraphie de SLE": [],
    "Technologie et génie": [],
}

# Qualité de la correspondance : 'directe' (même intitulé ou équivalent évident) / 'approchée' (cours voisin, à relire)
APPROCHEES = {"Mécanique", "Législation sociale et organisation du tourisme", "Législation fiscale et sociale", "Électricité", "Esthétique",
              "Législation", "Hygiène", "Technologie du pétrole", "Sécurité pétrolière", "Santé et sécurité du travail", "Géologie générale",
              "Comptabilité", "Levés géologiques", "Levés géochimiques", "Levés géophysiques", "Technologie machines", "Technologie meubles",
              "Biologie (anatomie, physiologie)", "Anatomie et physiologie", "Technologie", "Chimie appliquée", "Physique appliquée",
              "Technologie de soudure", "Organes de transmission", "Conservation des produits agricoles", "Contrôle de fabrication", "Génie industriel",
              "Économie alimentaire", "Hygiène alimentaire et nutrition", "Enquête nutritionnelle", "Gestion et administration", "Biologie appliquée",
              "Technique de laboratoire et chimie", "Dendrologie", "Sylviculture", "Législation forestière", "Comptabilité hôtelière", "Direction des travaux",
              "Technologie générale", "Histoire de l'art", "Tourisme", "Économie générale", "Économie de l'entreprise", "Sociologie et animation des loisirs",
              "Conservation des ressources naturelles", "Biologie animale", "Circuits logiques", "Informatique et microprocesseur", "Éléments de génie métallurgique",
              "Exploitation des mines à ciel ouvert", "Exploitation des mines souterraines", "Microbiologie"}


def cours(opt: str, nom: str) -> dict | None:
    for v in SRC.values():
        if v["opt"] == opt and v["cours"] == nom and v.get("items"):
            return v
    return None


def chapitres(c: dict) -> list[str]:
    out = []
    for it in c["items"]:
        if not it.startswith("- "):
            continue
        t = it[2:]
        t = re.sub(r"^(chapitre|ch\.?)\s*\d+\s*[:\-—–.]\s*", "", t, flags=re.I).strip()
        t = t[0].upper() + t[1:] if t else t
        if t and t.lower() not in ("bilan et perspectives", "révision et évaluation", "rappel et récapitulation", "bilan professionnel et perspectives",
                                   "bilan professionnel et perspectives de carrière", "bilan de formation et perspectives professionnelles",
                                   "bilan et vision à long terme", "bilan et perspectives d'avenir", "bilan et agriculture durable"):
            out.append(t)
    # dédoublonner en conservant l'ordre
    vus, res = set(), []
    for t in out:
        if t.lower() not in vus:
            vus.add(t.lower())
            res.append(t)
    return res


disciplines_e32 = {d for (lib, nb, ns, dur, quotas) in e32.EPREUVES.values() for d, _, _ in quotas}
lignes, manquantes, couvertes = [], [], []
for disc, sources in CORRESPONDANCE.items():
    if disc not in disciplines_e32:
        print("ATTENTION : discipline hors E.32 :", disc)
    chaps, origines = [], []
    for opt, nom in sources:
        c = cours(opt, nom)
        if c:
            for ch in chapitres(c):
                if ch.lower() not in {x.lower() for x in chaps}:
                    chaps.append(ch)
            origines.append(f"{nom} ({opt})")
    if not chaps:
        manquantes.append(disc)
        continue
    qual = "approchée" if disc in APPROCHEES else "directe"
    src = f"manuel conforme au programme EPST, 4e humanités — {' + '.join(origines)} — correspondance {qual}, à confirmer"
    for ch in chaps:
        lignes.append({"discipline": disc, "sous_discipline": None, "chapitre": ch, "poids": 1, "source": src})
    couvertes.append((disc, len(chaps), qual))

out = RACINE / "docs/programmes/complement_manuels.json"
out.write_text(json.dumps({"source": "manuels-scolaires-rdc.com, sommaires des manuels de 4e année des humanités (25/11/2026)", "programme": lignes},
                          ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(lignes)} chapitres pour {len(couvertes)} disciplines ; sans source : {manquantes}")
for d, n, q in sorted(couvertes):
    print(f"  {d}: {n} ({q})")
