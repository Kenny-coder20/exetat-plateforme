"""Données de configuration : E.32 session 2026, option 1.02 Sciences, et programmes officiels.

Sources des programmes (Ministère de l'EPST, RDC) :
- Mathématiques, SVT, SPTTIC : Programmes éducatifs 4e année des Humanités scientifiques (6e secondaire), DIPROMAD, 2021
  (edu-nc.gouv.cd/national-programmes).
- Éducation civique et morale : Programme national ECM secondaire, 6e année, 2007 (edu-nc.gouv.cd).
- Histoire : Programme national d'histoire, 6e année, 2005 (edu-nc.gouv.cd).
- Géographie : Programme national de géographie, 6e année, 2005 (edu-nc.gouv.cd).
- Philosophie : programme officiel NON trouvé en ligne ; liste RECONSTITUÉE à partir des cours de 6e en usage,
  à confirmer par un inspecteur (source = 'reconstitue').
Un CSV officiel peut toujours remplacer la liste : `python -m app.cli programme programme.csv`.
"""
from .db import connect

from .e32 import EPREUVES as E32_EPREUVES, EPREUVES_ACTIVES, FAMILLES, OPTIONS as E32_OPTIONS, SESSION

O21 = "officiel 2021"; O07 = "officiel 2007"; O05 = "officiel 2005"; O09 = "officiel 2009"; O16 = "officiel 2016"; OEL = "officiel (électricité)"; REC = "reconstitue"

# (discipline, sous_discipline, chapitre, poids, source)
PROGRAMME = [
    # ---- Mathématiques (MM6.1–6.31, regroupés)
    ("Mathématiques", None, "Nombres complexes : construction, représentations, équations (MM6.1–6.3)", 2, O21),
    ("Mathématiques", None, "Fonctions logarithmiques et exponentielles : étude, dérivées (MM6.4–6.5)", 2, O21),
    ("Mathématiques", None, "Équations, inéquations et applications log-exp (MM6.6–6.8)", 2, O21),
    ("Mathématiques", None, "Développement en série des fonctions usuelles (MM6.9)", 1, O21),
    ("Mathématiques", None, "Différentielle, primitives, intégration (MM6.10–6.12)", 2, O21),
    ("Mathématiques", None, "Applications géométriques de l'intégrale (MM6.13)", 1, O21),
    ("Mathématiques", None, "Probabilités (MM6.14)", 1, O21),
    ("Mathématiques", None, "Statistiques : paramètres de dispersion, lois de distribution (MM6.15–6.16)", 1, O21),
    ("Mathématiques", None, "Lieux géométriques et coniques : éléments focaux, tangentes, asymptotes, sommets (MM6.17–6.23)", 2, O21),
    ("Mathématiques", None, "Similitudes planes (MM6.24)", 0.5, O21),
    ("Mathématiques", None, "Géométrie de l'espace : plans, droites, rabattement, relèvement, rotations (MM6.25–6.31)", 1.5, O21),
    # ---- SVT
    ("SVT", "Biologie", "Cytologie : cycle cellulaire, anomalies chromosomiques (MSVT6.1–6.2)", 1, O21),
    ("SVT", "Biologie", "Reproduction humaine : cycle menstruel, fécondation (MSVT6.3–6.5)", 1.5, O21),
    ("SVT", "Biologie", "Immunologie : système immunitaire, dysfonctionnements, aides à la réponse (MSVT6.6–6.8)", 1.5, O21),
    ("SVT", "Biologie", "Génétique : mono- et dihybridisme, interactions géniques (MSVT6.9–6.13)", 1.5, O21),
    ("SVT", "Biologie", "Génétique humaine : hérédité liée au sexe et autosomale (MSVT6.14–6.15)", 1, O21),
    ("SVT", "Biologie", "Hérédité et probabilités, test du khi-carré, théorie chromosomique (MSVT6.16–6.20)", 0.5, O21),
    ("SVT", "Écologie", "Concepts écologiques, adaptabilité, écologie et autres sciences (MSVT6.23–6.25)", 1, O21),
    ("SVT", "Écologie", "Écosystèmes : interdépendance, limites, dynamique (MSVT6.26–6.29)", 2, O21),
    ("SVT", "Écologie", "Cycles biogéochimiques, biomes (MSVT6.30–6.31)", 1, O21),
    ("SVT", "Écologie", "Énergies renouvelables, biogéodiversité (MSVT6.32–6.33)", 1, O21),
    ("SVT", "Géologie & Évolution", "Évolution : histoire de l'évolution, étapes de l'évolution de l'homme (MSVT6.21)", 2, O21),
    ("SVT", "Géologie & Évolution", "Chronologie géologique (MSVT6.22)", 1, O21),
    # ---- Chimie (MSPC)
    ("Chimie", None, "Solutions : concentration, préparation d'une solution titrée (MSPC6.1)", 1, O21),
    ("Chimie", None, "Laboratoire : matériel et sécurité (MSPC6.2–6.3)", 0.5, O21),
    ("Chimie", None, "Titrages volumétriques : acido-basique, précipitation, oxydoréduction (MSPC6.4–6.6)", 1.5, O21),
    ("Chimie", None, "Électrochimie : potentiel redox, pile (MSPC6.7)", 1, O21),
    ("Chimie", None, "Atome : constituants, modèles, nombres quantiques, structure électronique (MSPC6.8–6.9)", 1, O21),
    ("Chimie", None, "Noyau atomique : radioactivité, énergie nucléaire, radio-isotopes (MSPC6.10–6.12)", 1, O21),
    ("Chimie", None, "Séparation et identification : chromatographie, cations, anions (MSPC6.13–6.15)", 0.5, O21),
    ("Chimie", None, "Préparation de produits de consommation : indicateur, peinture (MSPC6.16–6.17)", 0.5, O21),
    # ---- Physique (MSP)
    ("Physique", None, "Cinématique : MRU, MRUV, chute libre, mouvements circulaires (MSP6.1–6.5)", 1.5, O21),
    ("Physique", None, "Dynamique : lois de Newton, balistique, force centripète, moments d'inertie (MSP6.6–6.9)", 1.5, O21),
    ("Physique", None, "Poids et attraction universelle, frottements, ascenseurs, plan incliné, résistance de l'air (MSP6.10–6.14)", 1, O21),
    ("Physique", None, "Énergie mécanique, quantité de mouvement, moment cinétique, volant, marteau (MSP6.15–6.19)", 1, O21),
    ("Physique", None, "Thermodynamique et moteurs à combustion interne (MSP6.20–6.21)", 0.5, O21),
    ("Physique", None, "Oscillateurs et pendules (MSP6.22–6.28)", 1, O21),
    ("Physique", None, "Ondes : électromagnétiques, interférences, ondes stationnaires, acoustique, effet Doppler (MSP6.29–6.35)", 1, O21),
    ("Physique", None, "Courant alternatif : lois d'Ohm, circuits RLC, puissance et transformateur (MSP6.36–6.38)", 1, O21),
    # ---- TIC (MTIC)
    ("TIC", None, "Réseaux informatiques : généralités, LAN filaire, sans fil, client-serveur (MTIC6.1–6.4)", 1.5, O21),
    ("TIC", None, "Réseaux sociaux et sécurité informatique (MTIC6.5–6.6)", 1, O21),
    ("TIC", None, "Big data, objets connectés, algorithmes alpha-bêta, intelligence artificielle (MTIC6.7–6.9)", 0.5, O21),
    # ---- Civisme (Éducation civique et morale, 6e année, 2007)
    ("Civisme", None, "Connaissance de soi et du milieu social ; conscience (socialisée, critique, réformatrice, transformatrice)", 1, O07),
    ("Civisme", None, "Démocratie : partis politiques, groupes de pression, élections", 1.5, O07),
    ("Civisme", None, "Constitution : rôle, types, constitutions de la RDC, institutions, formes de l'État", 1.5, O07),
    ("Civisme", None, "Défense des droits humains : instruments juridiques, justice nationale et internationale", 1, O07),
    ("Civisme", None, "Code de la route : assurances et sociétés d'assurance", 0.5, O07),
    ("Civisme", None, "Morale : vertus morales, sociales et civiques ; services civiques", 1, O07),
    ("Civisme", None, "Culture de la paix : prévention et résolution des conflits, organisations internationales", 1, O07),
    ("Civisme", None, "Droit à l'égalité : genre et équité ; travaux d'intérêt communautaire", 0.5, O07),
    # ---- Histoire (6e année, 2005)
    ("Histoire", None, "Introduction à l'histoire : objet, origines de l'homme, sources, archives", 1, O05),
    ("Histoire", None, "Critique historique : heuristique, critique externe, critique interne, synthèse", 0.5, O05),
    ("Histoire", None, "Le monde après 1945 : ONU, accords internationaux", 1, O05),
    ("Histoire", None, "Afrique de 1945 à nos jours : décolonisation anglaise, française, portugaise ; problèmes de l'Afrique indépendante", 1.5, O05),
    ("Histoire", None, "Europe de 1945 à nos jours : blocs, Union européenne, coexistence pacifique", 1, O05),
    ("Histoire", None, "Asie de 1945 à nos jours : Inde, Chine, décolonisation de l'Asie", 1, O05),
    ("Histoire", None, "Grandes civilisations : négro-africaine, occidentale, islamique, latino-américaine, indienne, chinoise, japonaise", 0.5, O05),
    ("Histoire", None, "Rapports entre les parties du monde : capitalisme et socialisme, guerre froide, néocolonialisme, Tiers-monde", 1, O05),
    ("Histoire", None, "Synthèse de l'histoire du Congo : royaumes, traite, EIC, résistances, Congo belge, 1re et 2e Républiques, transition", 2.5, O05),
    ("Histoire", None, "Grands problèmes du monde contemporain : faim, désarmement, démographie, terrorisme", 1, O05),
    # ---- Géographie (6e année, 2005)
    ("Géographie", None, "RDC — nature et hommes : localisation, relief, climat, sols, végétation, hydrographie, population, villes", 2, O05),
    ("Géographie", None, "RDC — économie : agriculture, mines, énergie, industries, transports", 2, O05),
    ("Géographie", None, "RDC — services : commerce, enseignement, santé", 0.5, O05),
    ("Géographie", None, "RDC — étude régionale : Sud-Ouest, Centre, Est, Nord, Sud-Est", 1.5, O05),
    ("Géographie", None, "RDC — perspectives d'avenir : agriculture, industrie, infrastructures, tourisme, partenaires", 1, O05),
    ("Géographie", None, "Afrique contemporaine : présentation, l'Afrique dans le monde", 0.5, O05),
    ("Géographie", None, "États émergents africains : Afrique du Sud, Nigeria, Égypte", 1, O05),
    ("Géographie", None, "Afrique — perspectives : ressources, équipements, regroupements régionaux, partenaires et échanges", 1, O05),
    # ---- Philosophie (reconstitué — à confirmer)
    ("Philosophie", None, "Introduction : notion, objet, divisions et utilité de la philosophie ; philosophie, science, religion, sagesse", 1, REC),
    ("Philosophie", None, "Logique : concept, jugement, raisonnement, syllogisme, sophismes", 1.5, REC),
    ("Philosophie", None, "Théorie de la connaissance : sources, vérité et ses critères, méthodes des sciences", 1, REC),
    ("Philosophie", None, "Métaphysique et anthropologie philosophique : être, Dieu, âme, liberté, conscience, travail", 1, REC),
    ("Philosophie", None, "Morale : acte humain, conscience morale, valeurs, bonheur, responsabilité", 1, REC),
    ("Philosophie", None, "Philosophie sociale et politique : société, État, droit, justice, démocratie", 1, REC),
    ("Philosophie", None, "Philosophie africaine : Tempels, Kagame, Hountondji, Towa ; authenticité et développement", 1, REC),
    ("Philosophie", None, "Histoire de la philosophie : Antiquité, Moyen Âge, Temps modernes, époque contemporaine", 1.5, REC),
    # ---- Français (Programme national de français au secondaire, degré supérieur 5e–6e, 2009 — fichier local)
    ("Français", None, "Thèmes du degré supérieur : actualité, l'homme et la nature, l'homme et la société, activité humaine, valeurs morales, sentiments et émotions, l'homme et sa destinée", 1.5, O09),
    ("Français", None, "Étude de textes : compréhension, auteurs congolais, africains et français, courants et époques littéraires", 2, O09),
    ("Français", None, "Grammaire récapitulative : moyens d'expression, accords, modalités, phraséologie", 2, O09),
    ("Français", None, "Vocabulaire : mot propre, vocabulaire d'émotions et d'abstraction, synonymie, champs lexicaux", 1.5, O09),
    ("Français", None, "Orthographe et conjugaison", 1, O09),
    ("Français", None, "Expression orale : exposé-débat, conversation, lecture expressive", 1, O09),
    ("Français", None, "Expression écrite : lettre, article de presse, dissertation, genres de textes", 2, O09),
    # ---- Anglais (programme officiel non disponible en ligne — reconstitué, à confirmer)
    ("Anglais", None, "Reading comprehension: texts on everyday life, school, society, science", 2.5, REC),
    ("Anglais", None, "Grammar: tenses, modals, passive voice, reported speech, conditionals, relative clauses", 2.5, REC),
    ("Anglais", None, "Vocabulary: word formation, synonyms and antonyms, collocations, idioms", 2, REC),
    ("Anglais", None, "Functional English: letters, dialogues, descriptions, summaries", 2, REC),
    # ---- Pédagogie (Programme national de psychopédagogie, 6e année, 2009 — fichier local)
    ("Pédagogie", None, "Pédagogie : histoire de l'enseignement, dissertation pédagogique", 1, O09),
    ("Pédagogie", None, "Éducation : limites, anomalies, formes traditionnelles et nouvelles", 1, O09),
    ("Pédagogie", None, "L'enseignant : emploi du temps, calendrier scolaire, horaire des cours", 0.5, O09),
    ("Pédagogie", None, "Législation scolaire : sources, textes de référence, loi-cadre 86/005, finalités et structures de l'enseignement", 1.5, O09),
    ("Pédagogie", None, "Déontologie de l'enseignant : notion, exigences, conseils pratiques", 1, O09),
    ("Pédagogie", None, "Organisation scolaire : hiérarchie, documents administratifs et pédagogiques, tâches du chef d'établissement", 1, O09),
    ("Psychologie générale", None, "Psychologie générale : rappel des matières de 5e (sensation, perception, mémoire, intelligence, affectivité, personnalité)", 1, O09),
    ("Psychologie de l'enfant", None, "Psychologie du développement : importance, caractères, lois, auteurs (Wallon, Piaget)", 1, O09),
    ("Psychologie de l'enfant", None, "Stades du développement : période prénatale, première et deuxième enfance, âge scolaire", 1.5, O09),
    ("Psychologie de l'enfant", None, "Adolescence : pré-adolescence, puberté, crise d'originalité, orientation professionnelle", 1, O09),
    ("Psychologie de l'enfant", None, "Développement du langage et du jeu", 0.5, O09),
    ("Psychologie de l'enfant et de l'adolescent", None, "Psychologie du développement de l'enfant et de l'adolescent (programme 2009, 6e année)", 1, O09),
    ("Didactique générale", None, "Modes d'enseignement traditionnels et modernes : travail individualisé (plan Dalton, Winnetka), travail en équipe, méthode des projets de Kilpatrick, travail collectif", 2, O09),
    ("Didactique générale", None, "Récapitulation de la didactique générale et stage", 1, O09),
    ("Didactique des disciplines", None, "Marche d'une leçon : éducation civique, environnement, étude du milieu, histoire, géographie, sciences", 1.5, O09),
    ("Didactique des disciplines", None, "Marche d'une leçon : dessin (d'après nature, d'imagination, d'ornementation, de mémoire), chant, éducation physique, travaux manuels", 1, O09),
    # ---- Informatique (Curriculum national des humanités techniques commerciales, secrétariat-administration, 6e, 2016 — fichier local)
    ("Informatique", None, "Tableur : graphiques, base de données Excel, fonctions statistiques (minimum, maximum, moyenne, somme, écart type)", 1.5, O16),
    ("Informatique", None, "Publication assistée : Publisher, cartes de visite, affiches, zones de texte, WordArt", 1, O16),
    ("Informatique", None, "Traitement de texte avancé et correspondance administrative", 1, O16),
    ("Informatique", None, "Messagerie, Internet et sécurité des données du bureau", 0.5, O16),
    # ---- Électricité (Programme national d'électricité, 6e année — fichier local, en-têtes de chapitres)
    ("Machines électriques", None, "Génératrices à courant continu : principe, enroulement induit, fonctionnement, couple, rendement, couplage", 1.5, OEL),
    ("Machines électriques", None, "Transformateurs : parfait, réel, rendement, couplage, triphasés", 1.5, OEL),
    ("Machines électriques", None, "Redresseurs et champs tournants ; moteurs synchrones et asynchrones", 1.5, OEL),
    ("Applications électriques", None, "Éclairage, production, transport et distribution de l'énergie électrique, protection des réseaux", 1.5, OEL),
    ("Applications électriques", None, "Traction électrique, soudure électrique, fours électriques", 1, OEL),
    ("Applications électriques", None, "Installations : avant-projet de force motrice, schémas, sous-stations, tableaux de comptage", 1, OEL),
]

# Alias : « Biologie » et « Écologie » des épreuves M.06, M.09, M.10, M.12, M.18 reprennent les chapitres des
# sous-disciplines SVT du programme 2021 (le niveau attendu dans ces options est plus léger : les enseignants ajustent).
PROGRAMME += [("Biologie", None, ch, p, src) for d, sd, ch, p, src in PROGRAMME if d == "SVT" and sd == "Biologie"]
PROGRAMME += [("Écologie", None, ch, p, src) for d, sd, ch, p, src in PROGRAMME if d == "SVT" and sd == "Écologie"]


def seed(replace_programme: bool = False) -> None:
    with connect() as con:
        for code, (nom, _eps) in E32_OPTIONS.items():
            con.execute(
                "INSERT INTO options(code, nom, famille, session) VALUES(?,?,?,?) "
                "ON CONFLICT(code) DO UPDATE SET nom=excluded.nom, famille=excluded.famille, session=excluded.session",
                (code, nom, FAMILLES[code.split(".")[0]], SESSION),
            )
        con.execute("DELETE FROM option_epreuves")
        con.execute("DELETE FROM quotas")
        for code, (lib, nb, ns, h, quotas) in E32_EPREUVES.items():
            con.execute(
                "INSERT INTO epreuves(code, libelle, nb_items, nb_series, duree_h, actif) VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(code) DO UPDATE SET libelle=excluded.libelle, nb_items=excluded.nb_items, "
                "nb_series=excluded.nb_series, duree_h=excluded.duree_h, actif=excluded.actif",
                (code, lib, nb, ns, h, 1 if code in EPREUVES_ACTIVES else 0),
            )
            for k, (disc, sous, n) in enumerate(quotas, 1):
                con.execute("INSERT INTO quotas(epreuve_code, ordre, discipline, sous_discipline, nb_items) VALUES(?,?,?,?,?)",
                            (code, k, disc, sous, n))
        for opt, (nom, eps) in E32_OPTIONS.items():
            for jour, code in enumerate(eps, 1):
                con.execute("INSERT INTO option_epreuves(option_code, jour, epreuve_code) VALUES(?,?,?)", (opt, jour, code))
        n = con.execute("SELECT COUNT(*) AS n FROM programme").fetchone()["n"]
        n_off = con.execute("SELECT COUNT(*) AS n FROM programme WHERE source LIKE 'officiel%' AND discipline='Biologie'").fetchone()["n"]
        if n == 0 or replace_programme or n_off == 0:
            con.execute("DELETE FROM programme")
            con.executemany(
                "INSERT INTO programme(discipline, sous_discipline, chapitre, poids, source) VALUES(?,?,?,?,?)",
                PROGRAMME,
            )


def import_programme(path: str) -> int:
    """Remplace le programme par un CSV officiel : discipline,sous_discipline,chapitre,poids."""
    import csv

    with open(path, encoding="utf-8", newline="") as f, connect() as con:
        lignes = list(csv.DictReader(f))
        con.execute("DELETE FROM programme")
        con.executemany(
            "INSERT INTO programme(discipline, sous_discipline, chapitre, poids, source) VALUES(?,?,?,?,'officiel')",
            [
                (l["discipline"].strip(), (l.get("sous_discipline") or "").strip() or None,
                 l["chapitre"].strip(), float(l.get("poids") or 1))
                for l in lignes
            ],
        )
        return len(lignes)
