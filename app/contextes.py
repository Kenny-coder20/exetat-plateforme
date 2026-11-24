"""Variété des micro-contextes : formes d'entrée et univers attribués item par item.

Sans contrainte, les modèles produisent le même moule (« Dans une classe de Lubumbashi, un élève… »). On impose donc
dans la commande, pour chaque item, une FORME d'entrée (par quoi la situation commence) et un UNIVERS (où elle se
passe), tirés sans répétition dans une série, avec un plafond de lieux nommés et une part d'items sans personnage.
"""
from __future__ import annotations

import random

# Par quoi la situation entre en matière. Les formes « sans personnage » commencent par un objet, un document, une donnée.
FORMES = [
    ("un document à lire : étiquette, notice, facture, affiche, bulletin, extrait de presse, panneau", False),
    ("une donnée brute : relevé, mesure, tableau de chiffres, graphique décrit en une phrase", False),
    ("un objet du quotidien observé de près (sans personne nommée)", False),
    ("un phénomène observé dans la nature ou la ville, décrit comme un constat", False),
    ("un court dialogue de deux répliques entre deux personnes (métier ou lien précisé, pas d'élève)", True),
    ("une décision à prendre par un professionnel (artisan, infirmière, commerçante, pêcheur, chauffeur, agronome…)", True),
    ("une consigne de terrain ou un protocole suivi par une équipe", True),
    ("un événement collectif : marché, cérémonie, match, chantier, récolte, panne, inondation", True),
    ("une question posée par un enfant ou un grand-parent dans une famille", True),
    ("une comparaison entre deux options (deux appareils, deux trajets, deux offres, deux méthodes)", False),
    ("une erreur à repérer dans un calcul, un raisonnement ou un document déjà rédigé", False),
    ("une règle ou un texte officiel appliqué à un cas concret (sans personnage nommé)", False),
    ("une anecdote historique ou un fait attesté, raconté sobrement", False),
    ("une scène de travail observée (atelier, laboratoire, champ, cuisine, chantier, garage, studio)", True),
]

# Où cela se passe. Mélange de lieux congolais (sans excès de grandes villes), d'univers sans géographie et d'univers rares.
UNIVERS = [
    "marché de quartier", "atelier de couture", "garage de mécanique", "salon de coiffure", "pharmacie", "centre de santé rural",
    "pirogue sur un fleuve", "plantation de manioc", "étang piscicole", "scierie", "boulangerie", "cybercafé",
    "station de radio communautaire", "stade de football", "chorale ou orchestre", "chantier d'un pont", "transport en commun (bus, moto-taxi)",
    "gare ou port fluvial", "centrale hydroélectrique", "panneau solaire d'un village", "élevage de volailles", "bureau d'un notaire",
    "tribunal de paix", "mairie ou commune", "bureau de vote", "poste frontière", "parc national", "mine artisanale",
    "cuisine familiale", "veillée au village", "mariage coutumier", "marché de poisson séché", "cimetière communal",
    "studio de musique", "terrain de basket", "brasserie", "savonnerie artisanale", "bibliothèque", "laboratoire d'analyses",
    "cabinet dentaire", "tour de télécommunication", "chantier routier", "coopérative agricole", "banque ou mobile money",
    "voyage en avion intérieur", "éclipse ou saison des pluies", "jardin potager", "poulailler", "forge", "imprimerie",
    "observatoire météo", "camp de scouts", "carrière de sable", "fabrique de briques", "moulin à maïs", "cantine",
    "espace sans lieu précis (la situation se suffit à elle-même)", "espace sans lieu précis (la situation se suffit à elle-même)",
]

# Lieux nommés autorisés, avec rotation : grandes villes, villes moyennes, territoires, cours d'eau, régions naturelles.
LIEUX = [
    "Kinshasa", "Lubumbashi", "Goma", "Kisangani", "Bukavu", "Kananga", "Mbuji-Mayi", "Matadi", "Kikwit", "Kolwezi",
    "Mbandaka", "Kindu", "Uvira", "Boma", "Bunia", "Isiro", "Gemena", "Kalemie", "Tshikapa", "Likasi", "Butembo", "Beni",
    "Inongo", "Lisala", "Kenge", "Idiofa", "Kamina", "Kabinda", "Lodja", "Mwene-Ditu", "Zongo", "Moanda",
    "le fleuve Congo", "le lac Tanganyika", "le lac Kivu", "la rivière Kasaï", "la rivière Lualaba", "le Mayombe",
    "le plateau des Batéké", "la cuvette centrale", "les Virunga", "le Katanga", "le Kwilu", "l'Ituri", "le Sankuru",
]


def plan_contextes(n: int, graine: int | None = None) -> list[dict]:
    """Attribue à chacun des n items une forme, un univers, et décide s'il nomme un lieu et s'il met en scène quelqu'un.

    Règles : pas deux fois la même forme ni le même univers dans une série (tant que possible) ; au plus un item sur
    trois nomme un lieu ; au moins un item sur trois ne met en scène aucune personne ; jamais « un élève » ou « un
    professeur » comme personnage par défaut (ils restent possibles une fois par série au maximum).
    """
    rnd = random.Random(graine)
    formes = FORMES[:]
    rnd.shuffle(formes)
    univers = UNIVERS[:]
    rnd.shuffle(univers)
    lieux = LIEUX[:]
    rnd.shuffle(lieux)
    nb_lieux = max(1, n // 3) if n >= 2 else 1
    idx_lieux = set(rnd.sample(range(n), min(nb_lieux, n)))
    plan = []
    for k in range(n):
        forme, personnage = formes[k % len(formes)]
        u = univers[k % len(univers)]
        plan.append({
            "forme": forme,
            "univers": u,
            "personnage": personnage,
            "lieu": lieux[k % len(lieux)] if k in idx_lieux else None,
        })
    return plan


def decrire(p: dict) -> str:
    s = f"forme d'entrée : {p['forme']} ; univers : {p['univers']}"
    s += f" ; lieu nommé : {p['lieu']}" if p["lieu"] else " ; AUCUN nom de ville ni de région (le lieu reste implicite ou générique)"
    s += " ; avec un ou deux personnages (métier ou lien précisé)" if p["personnage"] else " ; SANS personnage : la situation part d'un objet, d'un document ou d'un constat"
    return s


CONSIGNE_VARIETE = """VARIÉTÉ DES CONTEXTES (obligatoire)
- Interdit : ouvrir plusieurs items par le même moule (« Dans une classe de … », « Un élève de … », « Un professeur demande … »). Les mots « élève », « professeur », « école », « classe », « devoir » n'apparaissent que dans UN item au plus par série, et jamais dans deux items consécutifs.
- Chaque item suit la forme d'entrée, l'univers, la règle de lieu et la règle de personnage indiqués dans son plan. Si le plan dit « sans personnage », la première phrase décrit un objet, un document, une mesure ou un constat, pas quelqu'un.
- Si l'univers tiré ne se prête vraiment pas au chapitre, garde la forme d'entrée et les règles de lieu et de personnage, et choisis un univers voisin, jamais scolaire ; ne retombe pas sur l'école.
- Les lieux nommés ne dépassent pas un item sur trois ; les autres restent sans géographie (« une boutique », « un dispensaire », « au bord d'une rivière ») ou se passent dans un univers qui se suffit à lui-même.
- Les personnages, quand il y en a, ont un métier ou un rôle précis et varié (sage-femme, mécanicien, vendeuse de poisson, agent de la SNEL, arbitre, pêcheur, pharmacienne, chauffeur de bus, animatrice radio, géomètre, chef de chantier, menuisier, apiculteur, brasseur, notaire…), parfois un prénom congolais, jamais le même rôle deux fois dans la série.
- Varier aussi l'angle de la question : prévoir, vérifier, choisir, expliquer un constat, corriger une erreur, comparer, estimer un ordre de grandeur, décider.
- La situation doit être inédite et plausible ; le contexte fournit au moins une donnée utile à la résolution, et rien de décoratif.
"""
