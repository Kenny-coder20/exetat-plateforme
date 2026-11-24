"""Programme E.32 — Examen d'État, session ordinaire 2026 (Inspection générale, Ministère de l'EPST, RDC).

Transcription complète des 48 options. Une épreuve est identifiée par son code (M.xx) et PARTAGÉE entre
toutes les options qui la portent : M.01 (culture générale) sert aux options 1.01, 1.02, 1.03, 1.04, 5.01 et 5.02.
La banque d'items est donc organisée par épreuve, et chaque option y accède selon son propre calendrier.

Légende : M = épreuve à choix multiple ; Q = nombre d'items ; S = nombre de séries (0 = série unique « S.U. ») ;
H = durée en heures. Les quotas sont (discipline, nombre d'items) dans l'ordre de l'épreuve.
"""

SESSION = 2026

# code → (famille, nom)
FAMILLES = {
    "1": "Humanités littéraires et scientifiques", "2": "Humanités pédagogiques", "3": "Humanités commerciales",
    "4": "Humanités sociales", "5": "Humanités artistiques", "6": "Coupe et couture",
    "7": "Hôtellerie, accueil et tourisme", "8": "Humanités agricoles", "9": "Humanités techniques industrielles",
}

# code épreuve → (libellé court, nb_items, nb_series, durée_h, [(discipline, sous_discipline, nb)])
EPREUVES = {
    # ---- culture générale
    "M.01": ("Culture générale", 20, 4, 2, [("Civisme", None, 2), ("Géographie", None, 6), ("Histoire", None, 6), ("Philosophie", None, 6)]),
    "M.02": ("Culture générale (pédagogie)", 15, 4, 2, [("Civisme", None, 2), ("Géographie", None, 5), ("Histoire", None, 5), ("Philosophie", None, 3)]),
    "M.03": ("Culture générale (sans philosophie)", 15, 0, 2, [("Civisme", None, 3), ("Géographie", None, 6), ("Histoire", None, 6)]),
    "M.04": ("Déontologie et citoyenneté", 5, 4, 2, [("Déontologie professionnelle", None, 3), ("Éducation à la citoyenneté", None, 2)]),
    "M.05": ("Culture générale (musique)", 15, 0, 2, [("Civisme", None, 3), ("Géographie", None, 4), ("Histoire", None, 4), ("Philosophie", None, 4)]),
    "M.030": ("Culture générale (coiffure)", 15, 0, 2, [("Civisme", None, 3), ("Questions d'actualité", None, 5), ("Histoire de la coiffure", None, 7)]),
    "M.033": ("Culture générale (sociale)", 8, 2, 2, [("Civisme", None, 2), ("Doctrines sociales", None, 3), ("Histoire du travail et organisation professionnelle", None, 3)]),
    "M.034": ("Actualité et civisme", 5, 2, 1, [("Actualité", None, 3), ("Civisme", None, 2)]),
    "M.035": ("Culture générale (hôtellerie)", 6, 0, 1, [("Civisme", None, 2), ("Géographie touristique", None, 2), ("Histoire", None, 2)]),
    "M.036": ("Culture générale (agricole)", 5, 2, 1, [("Histoire", None, 1), ("Géographie", None, 2), ("Civisme", None, 2)]),
    "M.037": ("Civisme et actualité", 5, 2, 1, [("Civisme", None, 2), ("Actualité", None, 3)]),
    "M.038": ("Civisme, actualité, géographie, histoire", 5, 0, 1, [("Civisme", None, 2), ("Actualité", None, 1), ("Géographie", None, 1), ("Histoire", None, 1)]),
    "M.91": ("Culture générale (maternelle)", 15, 0, 2, [("Civisme", None, 2), ("Histoire", None, 5), ("Philosophie", None, 3), ("Hygiène", None, 5)]),
    "M.96": ("Culture générale (tourisme)", 20, 0, 3, [("Histoire", None, 6), ("Législation sociale et organisation du tourisme", None, 7), ("Économie générale", None, 3), ("Psychologie sociale", None, 4)]),
    # ---- épreuves de spécialité (jour 2)
    "M.45": ("Latin", 25, 2, 5, [("Latin", None, 25)]),
    "M.46": ("Mathématiques et SVT", 30, 4, 5, [("Mathématiques", None, 15), ("SVT", "Biologie", 7), ("SVT", "Écologie", 5), ("SVT", "Géologie & Évolution", 3)]),
    "M.48": ("Grec et latin", 25, 0, 5, [("Grec", None, 10), ("Latin", None, 15)]),
    "M.49": ("Sciences de l'éducation", 30, 4, 5, [("Didactique générale", None, 6), ("Didactique des disciplines", None, 4), ("Psychologie générale", None, 7), ("Psychologie de l'enfant", None, 4), ("Pédagogie", None, 9)]),
    "M.50": ("Sciences de l'éducation (EPS)", 30, 0, 5, [("Didactique des disciplines", None, 9), ("Psychologie de l'enfant et de l'adolescent", None, 8), ("Théorie de l'éducation physique et sportive", None, 8), ("Pédagogie", None, 5)]),
    "M.51": ("Sciences de l'éducation (normale)", 30, 0, 5, [("Didactique générale", None, 7), ("Didactique des disciplines", None, 4), ("Psychologie générale", None, 7), ("Psychologie de l'enfant", None, 4), ("Pédagogie", None, 8)]),
    "M.52": ("Gestion", 15, 4, 4, [("Comptabilité analytique de gestion", None, 6), ("Informatique", None, 3), ("Fiscalité", None, 2), ("Finances publiques", None, 2), ("Législation sociale", None, 2)]),
    "M.53": ("Secrétariat", 15, 0, 5, [("Informatique", None, 7), ("Législation sociale", None, 3), ("Organisation du bureau", None, 5)]),
    "M.56": ("Sciences sociales", 25, 2, 5, [("Démographie", None, 6), ("Législation sociale", None, 8), ("Psychologie appliquée", None, 5), ("Protection de l'enfance", None, 3), ("Déontologie", None, 3)]),
    "M.57": ("Arts plastiques", 30, 0, 5, [("Anatomie artistique", None, 7), ("Esthétique", None, 8), ("Filmologie", None, 5), ("Histoire de l'art", None, 5), ("Musicologie", None, 5)]),
    "M.58": ("Arts dramatiques", 30, 0, 5, [("Histoire du décor et du costume", None, 8), ("Histoire du théâtre", None, 7), ("Esthétique théâtrale", None, 15)]),
    "M.59": ("Musique", 30, 0, 5, [("Auditions musicales", None, 8), ("Histoire de la musique", None, 6), ("Théorie musicale", None, 9), ("Transposition", None, 7)]),
    "M.901": ("Esthétique et coiffure", 30, 0, 5, [("Technologie de la coiffure", None, 8), ("Technologie des soins esthétiques", None, 8), ("Cosmétologie", None, 5), ("Éducation plastique", None, 5), ("Éthique et déontologie", None, 4)]),
    "M.902": ("Coiffure", 30, 0, 5, [("Soins de beauté", None, 3), ("Coupe cheveux", None, 7), ("Coloration / décoloration", None, 5), ("Éducation plastique", None, 7), ("Soutien de coiffure", None, 8)]),
    "M.60": ("Coupe et couture", 20, 2, 5, [("Législation sociale", None, 3), ("Technologie de la spécialité", None, 7), ("Technologie des textiles", None, 7), ("Organisation du travail", None, 3)]),
    "M.61": ("Accueil", 25, 0, 5, [("Esthétique", None, 7), ("Législation sociale", None, 5), ("Organisation du bureau", None, 5), ("Psychologie sociale", None, 8)]),
    "M.62": ("Hôtellerie et restauration", 25, 0, 5, [("Technologie hôtelière", None, 5), ("Technologie du restaurant", None, 7), ("Œnologie et boissons", None, 4), ("Comptabilité hôtelière", None, 5), ("Diététique", None, 4)]),
    "M.63": ("Hébergement", 25, 0, 5, [("Technologie hôtelière", None, 5), ("Technologie culinaire", None, 5), ("Technologie du restaurant", None, 5), ("Hygiène alimentaire et nutrition", None, 3), ("Législation sociale", None, 2), ("Comptabilité hôtelière", None, 5)]),
    "M.97": ("Tourisme", 30, 0, 5, [("Tourisme", None, 10), ("Biologie animale", None, 5), ("Conservation des ressources naturelles", None, 6), ("Sociologie et animation des loisirs", None, 9)]),
    "M.64": ("Agriculture générale", 15, 2, 4, [("Agriculture", None, 5), ("Amélioration des plantes cultivées", None, 1), ("Génie rural", None, 1), ("Phytopathologie", None, 2), ("Technologie agricole", None, 1), ("Zootechnie", None, 2), ("Agrostologie", None, 1), ("Développement rural", None, 1), ("Entrepreneuriat", None, 1)]),
    "M.65": ("Pêche et navigation", 15, 0, 4, [("Technologie et génie", None, 1), ("Écologie", None, 2), ("Ichtyopathologie", None, 1), ("Ichtyologie", None, 2), ("Conservation", None, 1), ("Pisciculture", None, 3), ("Pêche", None, 2), ("Navigation", None, 1), ("Développement rural", None, 1), ("Entrepreneuriat", None, 1)]),
    "M.66": ("Vétérinaire", 15, 0, 4, [("Maladies parasitaires", None, 1), ("Maladies infectieuses", None, 1), ("Pathologie", None, 2), ("Obstétrique", None, 1), ("Pharmacologie", None, 1), ("Zootechnie", None, 3), ("Technologie", None, 1), ("Hygiène", None, 1), ("Chirurgie", None, 1), ("Cultures fourragères", None, 1), ("Développement rural", None, 1), ("Entrepreneuriat", None, 1)]),
    "M.67": ("Industries agricoles", 15, 0, 4, [("Technique de laboratoire et chimie", None, 2), ("Microbiologie", None, 2), ("Conservation des produits agricoles", None, 2), ("Contrôle de fabrication", None, 2), ("Génie industriel", None, 4), ("Toxicologie", None, 1), ("Développement rural", None, 1), ("Entrepreneuriat", None, 1)]),
    "M.68": ("Nutrition", 15, 0, 4, [("Diététique", None, 4), ("Technologie culinaire", None, 3), ("Économie alimentaire", None, 1), ("Microbiologie", None, 2), ("Anatomie et physiologie", None, 3), ("Enquête nutritionnelle", None, 1), ("Entrepreneuriat", None, 1)]),
    "M.69": ("Foresterie", 15, 0, 4, [("Aménagement forestier", None, 2), ("Industries du bois", None, 1), ("Sylviculture", None, 2), ("Inventaire forestier", None, 2), ("Exploitation forestière", None, 2), ("Pathologie forestière", None, 1), ("Dendrologie", None, 1), ("Dendrométrie", None, 1), ("Législation forestière", None, 1), ("Développement rural", None, 1), ("Entrepreneuriat", None, 1)]),
    "M.74": ("Mécanique", 20, 2, 5, [("Mécanique appliquée", None, 10), ("Résistance des matériaux et éléments des machines", None, 8), ("Construction mécanique", None, 2)]),
    "M.75": ("Électricité", 25, 2, 5, [("Applications électriques", None, 8), ("Machines électriques", None, 10), ("Mécanique appliquée", None, 7)]),
    "M.761": ("Construction", 25, 2, 5, [("Béton armé", None, 7), ("Procédés généraux de construction", None, 5), ("Résistance des matériaux", None, 7), ("Voies de communication", None, 4), ("Législation", None, 2)]),
    "M.762": ("Dessin de bâtiment", 25, 0, 5, [("Béton armé", None, 6), ("Procédés généraux de construction", None, 5), ("Résistance des matériaux", None, 6), ("Histoire d'architecture", None, 4), ("Législation", None, 4)]),
    "M.763": ("Plomberie", 25, 0, 5, [("Technologie", None, 9), ("Environnement", None, 4), ("Mécanique", None, 8), ("Législation", None, 4)]),
    "M.771": ("Chimie industrielle", 25, 0, 5, [("Chimie industrielle", None, 13), ("Physique industrielle", None, 7), ("Régulation", None, 5)]),
    "M.772": ("Mine et géologie", 25, 0, 5, [("Minéralogie", None, 5), ("Géologie générale", None, 5), ("Chimie industrielle", None, 4), ("Sécurité industrielle", None, 4), ("Résistance des matériaux", None, 2), ("Régulation", None, 5)]),
    "M.773": ("Métallurgie", 25, 0, 5, [("Métallurgie", None, 12), ("Éléments de génie métallurgique", None, 5), ("Régulation", None, 5), ("Physique industrielle", None, 3)]),
    "M.774": ("Mines et carrières", 25, 0, 5, [("Exploitation des mines souterraines", None, 8), ("Exploitation des mines à ciel ouvert", None, 7), ("Géologie", None, 5), ("Mécanique appliquée", None, 5)]),
    "M.775": ("Géologie", 25, 0, 5, [("Analyse des données géologiques", None, 10), ("Levés géologiques", None, 4), ("Levés géophysiques", None, 3), ("Levés géochimiques", None, 3), ("Santé et sécurité du travail", None, 5)]),
    "M.78": ("Électronique industrielle", 25, 0, 5, [("Électricité industrielle", None, 5), ("Électronique", None, 10), ("Radiotélévision", None, 5), ("Télécommunication", None, 2), ("Hyperfréquence", None, 1), ("Régulation", None, 2)]),
    "M.79": ("Imprimerie", 25, 0, 5, [("Technologie générale", None, 4), ("Composition", None, 4), ("Esthétique", None, 3), ("Machine typo", None, 4), ("Reprographie", None, 6), ("Machine offset", None, 4)]),
    "M.80": ("Commutation", 25, 0, 5, [("Circuits logiques", None, 2), ("Communication télégraphique", None, 7), ("Commutation téléphonique", None, 7), ("Électricité", None, 4), ("Électronique", None, 5)]),
    "M.81": ("Radio transmission", 25, 0, 5, [("Antennes et propagation", None, 4), ("Circuits logiques", None, 2), ("Courant porteur", None, 5), ("Électricité", None, 4), ("Électronique", None, 5), ("Émission et réception", None, 5)]),
    "M.82": ("Météorologie", 25, 0, 5, [("Climatologie générale", None, 11), ("Circuits logiques", None, 2), ("Électricité", None, 4), ("Télécommunication météo", None, 6), ("Radioélectricité", None, 2)]),
    "M.83": ("Aviation civile", 25, 0, 5, [("Service d'information aéronautique", None, 3), ("Aérotechnique", None, 3), ("Navigation aérienne", None, 4), ("Opération aérienne", None, 4), ("Règlement du transport aérien", None, 4), ("Réglementation de la circulation aérienne", None, 4), ("Sécurité et lutte contre l'incendie", None, 3)]),
    "M.84": ("Mécanique dessin", 25, 0, 5, [("Mécanique appliquée", None, 10), ("Résistance des matériaux et éléments des machines", None, 8), ("Technologie hydropneumatique", None, 5), ("Construction", None, 2)]),
    "M.85": ("Hydro-pneumatique", 25, 0, 5, [("Mécanique appliquée", None, 10), ("Résistance des matériaux et éléments des machines", None, 6), ("Organes de transmission", None, 7), ("Construction", None, 2)]),
    "M.86": ("Pétrochimie", 20, 0, 5, [("Technologie du pétrole", None, 6), ("Pétrochimie", None, 5), ("Gestion des stocks pétroliers", None, 3), ("Automation", None, 3), ("Sécurité pétrolière", None, 3)]),
    "M.87": ("Mécanique automobile", 20, 0, 5, [("Moteurs thermiques", None, 4), ("Électricité automobile", None, 4), ("Résistance des matériaux et éléments des machines", None, 5), ("Mécanique appliquée", None, 5), ("Construction mécanique", None, 2)]),
    "M.88": ("Construction métallique", 25, 0, 5, [("Technologie de soudure", None, 6), ("Construction métallique", None, 12), ("Résistance des matériaux", None, 5), ("Traçage de tôlerie et chaudronnerie", None, 2)]),
    "M.93": ("Sciences de l'éducation (maternelle)", 30, 0, 5, [("Didactique générale", None, 4), ("Didactique des disciplines", None, 7), ("Psychologie générale", None, 4), ("Psychologie de l'enfant", None, 10), ("Pédagogie", None, 5)]),
    "M.95": ("Menuiserie", 20, 0, 5, [("Technologie machines", None, 5), ("Technologie meubles", None, 5), ("Mécanique appliquée", None, 4), ("Résistance des matériaux", None, 4), ("Législation fiscale et sociale", None, 2)]),
    # ---- épreuves scientifiques et techniques (jour 3)
    "M.06": ("Biologie, mathématiques, physique", 20, 2, 4, [("Biologie", None, 6), ("Mathématiques", None, 8), ("Physique", None, 6)]),
    "M.07": ("SPTIC — Chimie, Physique, TIC", 15, 4, 4, [("Chimie", None, 6), ("Physique", None, 6), ("TIC", None, 3)]),
    "M.09": ("Biologie, mathématiques, physique (Latin-Math)", 20, 0, 4, [("Biologie", None, 3), ("Mathématiques", None, 14), ("Physique", None, 3)]),
    "M.10": ("Biologie, mathématiques, physique (pédagogie)", 20, 4, 4, [("Biologie", None, 6), ("Mathématiques", None, 8), ("Physique", None, 6)]),
    "M.11": ("Sciences (EPS)", 20, 0, 4, [("Biologie (anatomie, physiologie)", None, 10), ("Chimie", None, 3), ("Mathématiques", None, 4), ("Physique", None, 3)]),
    "M.12": ("Écologie, mathématiques, physique", 20, 0, 4, [("Écologie", None, 6), ("Mathématiques", None, 8), ("Physique", None, 6)]),
    "M.13": ("Économie et mathématiques (commerciale)", 15, 4, 3, [("Économie du développement", None, 5), ("Organisation des entreprises", None, 5), ("Mathématiques", None, 5)]),
    "M.14": ("Mathématiques et gestion (secrétariat)", 15, 0, 4, [("Mathématiques", None, 5), ("Organisation des entreprises", None, 5), ("Statistique", None, 3), ("Entrepreneuriat", None, 2)]),
    "M.16": ("Économie et sciences (sociale)", 20, 2, 4, [("Économie du développement", None, 7), ("Hygiène et sécurité du travail", None, 4), ("Mathématiques", None, 6), ("Physique", None, 3)]),
    "M.17": ("Mathématiques et physique (arts plastiques)", 15, 0, 3, [("Mathématiques", None, 8), ("Physique", None, 7)]),
    "M.18": ("Biologie et mathématiques", 15, 2, 3, [("Biologie", None, 7), ("Mathématiques", None, 8)]),
    "M.19": ("Économie, physique, secourisme (accueil)", 25, 0, 4, [("Économie de l'entreprise", None, 5), ("Économie financière", None, 5), ("Finances publiques et droit fiscal", None, 5), ("Physique", None, 5), ("Secourisme", None, 5)]),
    "M.20": ("Sciences (hôtellerie)", 15, 0, 3, [("Mathématiques", None, 5), ("Physique", None, 3), ("Chimie", None, 4), ("Microbiologie", None, 3)]),
    "M.21": ("Sciences (agricole)", 10, 2, 2, [("Chimie", None, 3), ("Physique", None, 3), ("Mathématiques", None, 4)]),
    "M.22": ("Mathématiques et technique (mécanique)", 25, 2, 4, [("Mathématiques", None, 10), ("Électricité générale", None, 7), ("Transmission hydraulique et pneumatique", None, 5), ("Organisation des entreprises", None, 3)]),
    "M.23": ("Mathématiques et technique (électricité)", 20, 2, 4, [("Mathématiques", None, 10), ("Automation", None, 3), ("Électronique", None, 4), ("Organisation des entreprises", None, 3)]),
    "M.241": ("Mathématiques et technique (construction)", 20, 2, 4, [("Mathématiques", None, 10), ("Électricité", None, 4), ("Outillage de chantier", None, 3), ("Organisation des entreprises", None, 3)]),
    "M.242": ("Direction des travaux (dessin de bâtiment)", 20, 0, 4, [("Direction des travaux", None, 10), ("Mathématiques", None, 6), ("Organisation des entreprises", None, 4)]),
    "M.243": ("Mathématiques et technique (plomberie)", 20, 0, 4, [("Électricité", None, 4), ("Calcul professionnel", None, 6), ("Mathématiques", None, 6), ("Organisation des entreprises", None, 4)]),
    "M.251": ("Mathématiques et métallurgie (chimie industrielle)", 25, 0, 4, [("Mathématiques", None, 10), ("Métallurgie", None, 12), ("Organisation des entreprises", None, 3)]),
    "M.252": ("Mathématiques et technique (mine et géologie)", 25, 0, 4, [("Mathématiques", None, 10), ("Métallurgie", None, 6), ("Technique graphique", None, 6), ("Organisation des entreprises", None, 3)]),
    "M.253": ("Mathématiques et technique (métallurgie)", 25, 0, 4, [("Mathématiques", None, 10), ("Métallographie", None, 7), ("Chimie industrielle", None, 5), ("Organisation des entreprises", None, 3)]),
    "M.254": ("Mathématiques et technique (mines et carrières)", 25, 0, 4, [("Mathématiques", None, 10), ("Mécanique des roches", None, 4), ("Organisation des entreprises", None, 3), ("Technique hydro-pneumatique", None, 3), ("Topographie", None, 3), ("Automation des mines", None, 2)]),
    "M.255": ("Mathématiques et technique (géologie)", 20, 0, 4, [("Mathématiques", None, 10), ("Instruments et équipements de diagraphie de SLE", None, 7), ("Entrepreneuriat", None, 3)]),
    "M.26": ("Mathématiques et technique (électronique)", 25, 0, 4, [("Mathématiques", None, 10), ("Automation", None, 8), ("Informatique et microprocesseur", None, 4), ("Organisation des entreprises", None, 3)]),
    "M.27": ("Mathématiques et calculation (imprimerie)", 25, 0, 4, [("Mathématiques", None, 10), ("Calculation", None, 12), ("Organisation des entreprises", None, 3)]),
    "M.28": ("Mathématiques et technique (commutation)", 25, 0, 4, [("Mathématiques", None, 10), ("Téléphonie générale", None, 6), ("Transmission télégraphique et numérique", None, 6), ("Organisation des entreprises", None, 3)]),
    "M.29": ("Mathématiques et technique (radio)", 25, 0, 4, [("Mathématiques", None, 10), ("Hyperfréquences", None, 7), ("Radiotélévision", None, 5), ("Organisation des entreprises", None, 3)]),
    "M.30": ("Mathématiques et météorologie", 25, 0, 4, [("Mathématiques", None, 10), ("Météorologie générale", None, 7), ("Météorologie spéciale", None, 2), ("Météorologie tropicale", None, 2), ("Notions d'informatique", None, 1), ("Organisation des entreprises", None, 3)]),
    "M.31": ("Mathématiques et aviation", 25, 0, 4, [("Mathématiques", None, 10), ("Circuits logiques", None, 3), ("Notions d'informatique", None, 4), ("Notions de droit aérien", None, 5), ("Organisation des entreprises", None, 3)]),
    "M.32": ("Mathématiques et électricité industrielle", 20, 0, 4, [("Mathématiques", None, 10), ("Électricité industrielle", None, 7), ("Organisation des entreprises", None, 3)]),
    "M.33": ("Mathématiques et chimie (pétrochimie)", 25, 0, 4, [("Mathématiques", None, 10), ("Physique industrielle", None, 5), ("Chimie", None, 7), ("Organisation des entreprises", None, 3)]),
    "M.34": ("Mathématiques et électronique (automobile)", 25, 0, 4, [("Mathématiques", None, 10), ("Automation", None, 3), ("Électronique", None, 9), ("Organisation des entreprises", None, 3)]),
    "M.35": ("Mathématiques et technique (construction métallique)", 25, 0, 4, [("Mathématiques", None, 10), ("Électricité", None, 7), ("Mécanique appliquée", None, 5), ("Organisation des entreprises", None, 3)]),
    "M.94": ("Mathématiques et menuiserie", 25, 0, 4, [("Mathématiques", None, 10), ("Menuiserie de bâtiment", None, 6), ("Comptabilité", None, 6), ("Organisation des entreprises", None, 3)]),
    "M.98": ("Mathématiques et tourisme", 20, 0, 4, [("Mathématiques", None, 7), ("Photographie", None, 2), ("Organisation des entreprises", None, 3), ("Informatique", None, 3), ("Géographie touristique", None, 5)]),
    "M.891": ("Sciences appliquées (esthétique)", 20, 0, 4, [("Mathématiques", None, 7), ("Physique appliquée", None, 4), ("Chimie appliquée", None, 4), ("Biologie appliquée", None, 5)]),
    "M.892": ("Sciences appliquées (coiffure)", 20, 0, 4, [("Mathématiques", None, 7), ("Biologie appliquée", None, 8), ("Gestion et administration", None, 5)]),
    "M.92": ("Exploration du milieu et sciences (maternelle)", 20, 0, 4, [("Exploration du milieu", None, 6), ("Mathématiques", None, 8), ("Physique", None, 4), ("Informatique", None, 2)]),
    # ---- langues (jour 4)
    "M.36": ("Langues", 20, 4, 4, [("Anglais", None, 9), ("Français", None, 11)]),
    "M.37": ("Langues (série unique)", 20, 0, 4, [("Anglais", None, 9), ("Français", None, 11)]),
    "M.38": ("Langues et correspondance commerciale", 10, 4, 2, [("Anglais", None, 3), ("Correspondance commerciale anglaise", None, 2), ("Correspondance commerciale française", None, 2), ("Français", None, 3)]),
    "M.39": ("Langues (sociale)", 12, 2, 3, [("Anglais", None, 4), ("Français", None, 8)]),
    "M.40": ("Langues (15 items)", 15, 2, 3, [("Anglais", None, 5), ("Français", None, 10)]),
    "M.41": ("Langues (hôtellerie)", 14, 0, 3, [("Anglais", None, 5), ("Français", None, 9)]),
    "M.42": ("Langues (agricole)", 5, 2, 2, [("Anglais", None, 2), ("Français", None, 3)]),
    "M.43": ("Langues (techniques)", 10, 2, 2, [("Anglais", None, 3), ("Français", None, 7)]),
    "M.44": ("Langues (télécommunications)", 10, 0, 2, [("Anglais", None, 2), ("Français", None, 8)]),
    "M.99": ("Langues (tourisme)", 15, 0, 3, [("Anglais", None, 7), ("Français", None, 8)]),
}

# option → (nom, [épreuve jour 1, jour 2, jour 3, jour 4])
OPTIONS = {
    "1.01": ("Latin-Philosophie", ["M.01", "M.45", "M.06", "M.36"]),
    "1.02": ("Sciences", ["M.01", "M.46", "M.07", "M.36"]),
    "1.03": ("Latin-Grec", ["M.01", "M.48", "M.06", "M.36"]),
    "1.04": ("Latin-Mathématique", ["M.01", "M.45", "M.09", "M.36"]),
    "2.01": ("Pédagogie générale", ["M.02", "M.49", "M.10", "M.36"]),
    "2.02": ("Éducation physique et sportive", ["M.03", "M.50", "M.11", "M.37"]),
    "2.03": ("Normale", ["M.02", "M.51", "M.12", "M.36"]),
    "2.04": ("Pédagogie maternelle", ["M.91", "M.93", "M.92", "M.36"]),
    "2.05": ("Pédagogie pré-scolaire", ["M.91", "M.93", "M.92", "M.37"]),
    "3.01": ("Commerciale et gestion", ["M.04", "M.52", "M.13", "M.38"]),
    "3.02": ("Secrétariat-Administration", ["M.04", "M.53", "M.14", "M.38"]),
    "4.01": ("Sociale", ["M.033", "M.56", "M.16", "M.39"]),
    "5.01": ("Arts plastiques", ["M.01", "M.57", "M.17", "M.37"]),
    "5.02": ("Arts dramatiques", ["M.01", "M.58", "M.18", "M.37"]),
    "5.03": ("Musique", ["M.05", "M.59", "M.10", "M.37"]),
    "5.04": ("Esthétique et coiffure", ["M.03", "M.901", "M.891", "M.37"]),
    "5.05": ("Coiffure", ["M.030", "M.902", "M.892", "M.37"]),
    "6.01": ("Coupe et couture", ["M.034", "M.60", "M.18", "M.40"]),
    "7.01": ("Hôtesse d'accueil", ["M.03", "M.61", "M.19", "M.36"]),
    "7.02": ("Hôtellerie et restauration", ["M.035", "M.62", "M.20", "M.41"]),
    "7.03": ("Hébergement", ["M.034", "M.63", "M.18", "M.40"]),
    "7.04": ("Tourisme", ["M.96", "M.97", "M.98", "M.99"]),
    "8.01": ("Agriculture générale", ["M.036", "M.64", "M.21", "M.42"]),
    "8.02": ("Pêche et navigation", ["M.036", "M.65", "M.21", "M.42"]),
    "8.03": ("Vétérinaire", ["M.036", "M.66", "M.21", "M.42"]),
    "8.04": ("Industries agricoles", ["M.036", "M.67", "M.21", "M.42"]),
    "8.05": ("Nutrition", ["M.036", "M.68", "M.21", "M.42"]),
    "8.06": ("Foresterie", ["M.036", "M.69", "M.21", "M.42"]),
    "9.01": ("Mécanique générale", ["M.037", "M.74", "M.22", "M.43"]),
    "9.02": ("Mécanique machines-outils", ["M.037", "M.74", "M.22", "M.43"]),
    "9.03": ("Électricité", ["M.037", "M.75", "M.23", "M.43"]),
    "9.04": ("Construction", ["M.037", "M.761", "M.241", "M.43"]),
    "9.05": ("Chimie industrielle", ["M.037", "M.771", "M.251", "M.43"]),
    "9.06": ("Électronique industrielle", ["M.037", "M.78", "M.26", "M.43"]),
    "9.07": ("Imprimerie", ["M.037", "M.79", "M.27", "M.43"]),
    "9.08": ("Commutation", ["M.038", "M.80", "M.28", "M.44"]),
    "9.09": ("Radio transmission", ["M.038", "M.81", "M.29", "M.44"]),
    "9.10": ("Météorologie", ["M.038", "M.82", "M.30", "M.44"]),
    "9.11": ("Aviation civile", ["M.038", "M.83", "M.31", "M.44"]),
    "9.12": ("Mécanique dessin", ["M.037", "M.84", "M.32", "M.43"]),
    "9.13": ("Hydro-pneumatique", ["M.037", "M.85", "M.32", "M.43"]),
    "9.14": ("Pétrochimie", ["M.037", "M.86", "M.33", "M.43"]),
    "9.15": ("Mécanique automobile", ["M.037", "M.87", "M.34", "M.43"]),
    "9.16": ("Construction métallique", ["M.037", "M.88", "M.35", "M.43"]),
    "9.17": ("Menuiserie", ["M.037", "M.95", "M.94", "M.43"]),
    "9.18": ("Mine et géologie", ["M.037", "M.772", "M.252", "M.43"]),
    "9.19": ("Métallurgie", ["M.037", "M.773", "M.253", "M.43"]),
    "9.20": ("Dessin de bâtiment", ["M.037", "M.762", "M.242", "M.43"]),
    "9.21": ("Plomberie (installation sanitaire)", ["M.037", "M.763", "M.243", "M.43"]),
    "9.22": ("Mines et carrières", ["M.037", "M.774", "M.254", "M.43"]),
    "9.23": ("Géologie", ["M.037", "M.775", "M.255", "M.43"]),
}

# Épreuves dont la banque est ouverte dans la plateforme (les autres sont déclarées, « bientôt »)
EPREUVES_ACTIVES = {
    "M.01", "M.46", "M.07",                      # option Sciences
    "M.02", "M.03", "M.05", "M.036",             # culture générale des autres options (mêmes matières que M.01)
    "M.49", "M.51", "M.93",                      # sciences de l'éducation
    "M.06", "M.09", "M.10", "M.12", "M.17", "M.18", "M.21",   # sciences des options non scientifiques
    "M.36", "M.37", "M.39", "M.40", "M.41", "M.42", "M.43", "M.44", "M.99",  # langues (anglais : programme reconstitué)
}


def verifier():
    """Contrôle de cohérence : chaque quota somme au nombre d'items annoncé ; chaque option référence des épreuves connues."""
    erreurs = []
    for code, (lib, n, s, h, quotas) in EPREUVES.items():
        tot = sum(q[2] for q in quotas)
        if tot != n:
            erreurs.append(f"{code} : quotas {tot} ≠ {n} items")
    for opt, (nom, eps) in OPTIONS.items():
        for e in eps:
            if e not in EPREUVES:
                erreurs.append(f"{opt} : épreuve {e} inconnue")
    return erreurs


if __name__ == "__main__":
    for e in verifier() or ["cohérent"]:
        print(e)
