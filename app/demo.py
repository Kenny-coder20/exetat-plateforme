"""Items de démonstration (rédigés à la main au gabarit de la charte, marqués version='demo').

Ils permettent de tester l'assemblage, l'export et l'app élève avant la première génération.
Le jour 3 (Chimie 6, Physique 6, TIC 3) est complet ; le jour 2 est volontairement partiel pour montrer
le message « banque insuffisante ».
"""
from .db import EPREUVE_PAR_DISCIPLINE_V1, connect, maintenant
from .generation import compter_mots

# (discipline, sous_discipline, chapitre, difficulte, titre, tige, [p1..p5], reponse, correction, erreurs)
ITEMS = [
    # ---------------- CHIMIE (6)
    ("Chimie", None, "Solutions et concentrations", "moyen",
     "Préparation d'une solution au laboratoire de l'école",
     "Au laboratoire de son école à Kinshasa, un élève dissout 5,85 g de chlorure de sodium NaCl dans de l'eau pour obtenir 500 mL de solution. On donne M(NaCl) = 58,5 g/mol. Quelle est la concentration molaire de la solution obtenue ?",
     ["0,1 mol/L", "0,2 mol/L", "0,05 mol/L", "11,7 mol/L", "0,01 mol/L"], 2,
     "n = m / M = 5,85 / 58,5 = 0,1 mol. V = 500 mL = 0,5 L. C = n / V = 0,1 / 0,5 = 0,2 mol/L.",
     "1 : volume pris pour 1 L ; 3 : n × V ; 4 : m / V sans passer par n ; 5 : erreur de puissance de dix"),
    ("Chimie", None, "Stœchiométrie et quantité de matière", "facile",
     "Masse molaire de l'eau pour un cours de chimie",
     "Dans une classe de Lubumbashi, le professeur demande de calculer la masse molaire de l'eau H2O à partir des masses molaires atomiques H = 1 g/mol et O = 16 g/mol. Un élève doit donner le résultat avant de doser une solution. Quelle est la masse molaire de l'eau ?",
     ["17 g/mol", "18 g/mol", "16 g/mol", "34 g/mol", "10 g/mol"], 2,
     "M(H2O) = 2 × M(H) + M(O) = 2 × 1 + 16 = 18 g/mol.",
     "1 : un seul H compté ; 3 : H oubliés ; 4 : 2 × 17 ; 5 : addition des numéros atomiques"),
    ("Chimie", None, "Acides, bases et pH", "moyen",
     "Contrôle de l'acidité d'un jus de fruits à Kisangani",
     "Une coopérative de Kisangani contrôle un jus de fruits avant la mise en bouteille. Le technicien mesure une concentration en ions H3O+ de 1 × 10^-3 mol/L à 25 °C. Il doit noter le pH sur la fiche de contrôle. Quelle valeur du pH doit-il inscrire ?",
     ["3", "-3", "11", "0,001", "10"], 1,
     "pH = -log[H3O+] = -log(10^-3) = 3. Le jus est acide (pH < 7).",
     "2 : signe oublié ; 3 : confusion avec pOH (14 - 3) ; 4 : concentration recopiée ; 5 : erreur d'exposant"),
    ("Chimie", None, "Oxydoréduction", "difficile",
     "Pile zinc-cuivre réalisée en travaux pratiques à Goma",
     "En travaux pratiques à Goma, des élèves réalisent une pile avec une lame de zinc dans une solution de Zn2+ et une lame de cuivre dans une solution de Cu2+, reliées par un pont salin. On donne les potentiels standard E°(Zn2+/Zn) = -0,76 V et E°(Cu2+/Cu) = +0,34 V. Quelle est la force électromotrice de la pile ?",
     ["0,42 V", "1,10 V", "-1,10 V", "0,34 V", "0,76 V"], 2,
     "La cathode est l'électrode de potentiel le plus élevé (cuivre). fem = E°(cathode) - E°(anode) = 0,34 - (-0,76) = 1,10 V. Le zinc s'oxyde, le cuivre se réduit.",
     "1 : soustraction des valeurs absolues ; 3 : électrodes inversées ; 4 et 5 : un seul potentiel retenu"),
    ("Chimie", None, "Chimie organique : hydrocarbures et fonctions", "facile",
     "Gaz butane utilisé pour la cuisine à Matadi",
     "Une famille de Matadi cuisine avec une bouteille de gaz butane. Sur l'étiquette, le gaz est présenté comme un alcane à quatre atomes de carbone. L'élève veut écrire sa formule brute pour un devoir. Quelle est la formule brute du butane ?",
     ["C4H8", "C4H10", "C4H6", "C3H8", "C4H12"], 2,
     "Formule générale des alcanes : CnH2n+2. Pour n = 4 : C4H10.",
     "1 : formule des alcènes CnH2n ; 3 : formule des alcynes ; 4 : propane ; 5 : erreur de comptage"),
    ("Chimie", None, "Stœchiométrie et quantité de matière", "difficile",
     "Combustion du charbon de bois dans un foyer amélioré à Bukavu",
     "À Bukavu, un ménage brûle 1,2 kg de charbon de bois, supposé constitué de carbone pur, dans un foyer amélioré selon C + O2 → CO2. On donne M(C) = 12 g/mol et M(CO2) = 44 g/mol. Quelle masse de dioxyde de carbone est rejetée dans l'air par cette combustion complète ?",
     ["1,2 kg", "3,2 kg", "4,4 kg", "0,33 kg", "44 kg"], 3,
     "n(C) = 1200 / 12 = 100 mol. La réaction est mole à mole : n(CO2) = 100 mol. m(CO2) = 100 × 44 = 4400 g = 4,4 kg.",
     "1 : masse conservée à tort ; 2 : masse de O2 consommé ; 4 : rapport inversé 12/44 ; 5 : confusion g/kg"),
    # ---------------- PHYSIQUE (6)
    ("Physique", None, "Électricité : loi d'Ohm, puissance, énergie", "facile",
     "Lampe alimentée par un panneau solaire dans un village du Kongo-Central",
     "Dans un village du Kongo-Central, une famille branche une lampe sur une batterie solaire de 12 V. La lampe a une résistance de 24 Ω et fonctionne normalement. Quelle intensité du courant traverse la lampe ?",
     ["2 A", "0,5 A", "288 A", "12 A", "0,2 A"], 2,
     "Loi d'Ohm : U = R × I donc I = U / R = 12 / 24 = 0,5 A.",
     "1 : R / U ; 3 : U × R ; 4 : U pris pour I ; 5 : erreur de division"),
    ("Physique", None, "Électricité : loi d'Ohm, puissance, énergie", "moyen",
     "Facture d'électricité d'un salon de coiffure à Kinshasa",
     "Un salon de coiffure de Kinshasa utilise un sèche-cheveux de 1 500 W pendant 2 heures par jour, 25 jours par mois. Le gérant veut estimer l'énergie consommée par cet appareil sur le mois pour vérifier sa facture SNEL. Quelle énergie mensuelle l'appareil consomme-t-il ?",
     ["3 kWh", "75 kWh", "37,5 kWh", "750 kWh", "30 kWh"], 2,
     "E = P × t = 1,5 kW × (2 × 25) h = 1,5 × 50 = 75 kWh.",
     "1 : un seul jour ; 3 : 1 h par jour ; 4 : erreur de conversion W/kW ; 5 : P oubliée"),
    ("Physique", None, "Mécanique : forces, mouvement, travail", "moyen",
     "Porteur de sacs au port de Kalemie",
     "Au port de Kalemie, un porteur soulève un sac de 40 kg du sol jusqu'à une hauteur de 1,5 m pour le charger dans un camion. On prend g = 10 N/kg. Quel travail le porteur fournit-il contre le poids du sac lors de cette montée ?",
     ["60 J", "600 J", "400 J", "6 000 J", "26,7 J"], 2,
     "Poids P = m × g = 40 × 10 = 400 N. Travail W = P × h = 400 × 1,5 = 600 J.",
     "1 : g oublié ; 3 : hauteur oubliée ; 4 : facteur 10 en trop ; 5 : division au lieu de multiplication"),
    ("Physique", None, "Optique géométrique", "difficile",
     "Loupe utilisée par un réparateur de téléphones à Mbuji-Mayi",
     "Un réparateur de téléphones de Mbuji-Mayi utilise une lentille convergente de distance focale 5 cm comme loupe. Il place un composant à 4 cm de la lentille pour l'observer. Quelle est la nature et la position de l'image obtenue ?",
     ["réelle, à 20 cm derrière la lentille", "virtuelle, à 20 cm devant la lentille", "virtuelle, à 2,2 cm devant la lentille", "réelle, à 2,2 cm derrière la lentille", "à l'infini"], 2,
     "Relation de conjugaison : 1/OA' - 1/OA = 1/f'. Avec OA = -4 cm et f' = 5 cm : 1/OA' = 1/5 - 1/4 = -1/20, donc OA' = -20 cm. L'image est virtuelle, droite, agrandie, à 20 cm devant la lentille : c'est le fonctionnement d'une loupe.",
     "1 : signe oublié ; 3 et 4 : 1/f' + 1/OA au lieu de la relation correcte ; 5 : confusion avec l'objet au foyer"),
    ("Physique", None, "Électromagnétisme et courant alternatif", "facile",
     "Tension du réseau domestique à Lubumbashi",
     "À Lubumbashi, un électricien mesure avec un voltmètre la tension du réseau domestique et lit 220 V. Il explique à un apprenti que cette valeur est la tension efficace du courant alternatif. Quelle est la tension maximale correspondante ?",
     ["220 V", "311 V", "155 V", "440 V", "110 V"], 2,
     "Umax = Ueff × √2 = 220 × 1,414 ≈ 311 V.",
     "1 : efficace confondue avec maximale ; 3 : division par √2 ; 4 : facteur 2 ; 5 : moitié de la tension"),
    ("Physique", None, "Ondes et son", "moyen",
     "Éclair et tonnerre observés pendant la saison des pluies à Kananga",
     "Pendant un orage à Kananga, une élève voit un éclair puis entend le tonnerre 6 secondes plus tard. Elle sait que le son se propage dans l'air à environ 340 m/s et que la lumière arrive quasi instantanément. À quelle distance l'éclair s'est-il produit ?",
     ["57 m", "2 040 m", "340 m", "20 400 m", "1 020 m"], 2,
     "d = v × t = 340 × 6 = 2 040 m, soit environ 2 km.",
     "1 : v / t ; 3 : temps oublié ; 4 : facteur 10 ; 5 : temps pris pour 3 s"),
    # ---------------- TIC (3)
    ("TIC", None, "Tableur : formules et graphiques", "facile",
     "Moyenne des notes dans le tableur du secrétariat d'une école",
     "Au secrétariat d'une école de Kinshasa, les notes d'un élève sont saisies dans un tableur dans les cellules B2 à B8. Le secrétaire veut afficher la moyenne de ces notes dans la cellule B9 sans la calculer à la main. Quelle formule doit-il saisir en B9 ?",
     ["=SOMME(B2:B8)", "=MOYENNE(B2:B8)", "=MOYENNE(B2;B8)", "=B2+B8/7", "=NB(B2:B8)"], 2,
     "La fonction MOYENNE appliquée à la plage B2:B8 (les deux-points désignent une plage) calcule la moyenne arithmétique.",
     "1 : somme au lieu de moyenne ; 3 : point-virgule = deux cellules seulement ; 4 : priorité des opérations fausse ; 5 : compte les cellules"),
    ("TIC", None, "Réseaux, Internet et sécurité numérique", "moyen",
     "Message suspect reçu par un enseignant de Goma",
     "Un enseignant de Goma reçoit un courriel au nom de sa banque qui lui demande de cliquer sur un lien et de saisir son mot de passe pour « débloquer son compte ». L'adresse de l'expéditeur ne correspond pas au domaine de la banque. De quelle menace informatique s'agit-il ?",
     ["un virus", "un hameçonnage (phishing)", "un pare-feu", "une mise à jour", "un rançongiciel"], 2,
     "Un message qui imite un organisme pour obtenir des identifiants est un hameçonnage. La bonne pratique : ne pas cliquer, vérifier l'adresse, contacter la banque directement.",
     "1 et 5 : logiciels malveillants, pas une tromperie par message ; 3 : outil de protection ; 4 : opération légitime"),
    ("TIC", None, "Traitement de texte et fichiers", "facile",
     "Taille d'un fichier à envoyer depuis un cybercafé de Kikwit",
     "Dans un cybercafé de Kikwit, un étudiant doit envoyer par courriel un rapport dont la taille affichée est 2 048 Ko. La messagerie limite les pièces jointes à 25 Mo. Il veut savoir si l'envoi passera. Quelle est la taille du fichier en mégaoctets ?",
     ["0,2 Mo", "2 Mo", "20 Mo", "204,8 Mo", "2 048 Mo"], 2,
     "1 Mo = 1 024 Ko, donc 2 048 Ko = 2 048 / 1 024 = 2 Mo. L'envoi passe largement.",
     "1 : division par 10 000 ; 3 : division par 100 ; 4 : division par 10 ; 5 : aucune conversion"),
    # ---------------- MATHÉMATIQUES (4, partiel)
    ("Mathématiques", None, "Géométrie plane", "moyen",
     "Coût d'une clôture dans une parcelle de Kinshasa",
     "Un parent veut clôturer une parcelle rectangulaire de 25 m sur 15 m à Kinshasa. Le grillage coûte 12 000 FC le mètre et il laisse un portail de 4 m sans grillage. Quel montant doit-il prévoir pour le grillage ?",
     ["912 000 FC", "960 000 FC", "4 452 000 FC", "456 000 FC", "1 008 000 FC"], 1,
     "Périmètre = 2 × (25 + 15) = 80 m. Longueur grillagée = 80 - 4 = 76 m. Coût = 76 × 12 000 = 912 000 FC.",
     "2 : portail oublié ; 3 : aire au lieu du périmètre ; 4 : demi-périmètre ; 5 : portail ajouté"),
    ("Mathématiques", None, "Probabilités", "facile",
     "Tirage au sort d'un délégué de classe à Kolwezi",
     "Dans une classe de Kolwezi de 40 élèves, dont 16 filles, le professeur tire au sort un délégué en piochant un nom dans une urne où chaque élève figure une fois. Les élèves veulent connaître la chance qu'une fille soit désignée. Quelle est la probabilité que le délégué soit une fille ?",
     ["0,16", "0,4", "0,6", "0,24", "0,25"], 2,
     "P = nombre de cas favorables / nombre de cas possibles = 16 / 40 = 0,4.",
     "1 : 16 lu comme 16 % ; 3 : probabilité d'un garçon ; 4 : 24/100 ; 5 : 1/4 approximatif"),
    ("Mathématiques", None, "Exponentielles et logarithmes", "difficile",
     "Croissance d'une population de poissons dans un étang piscicole à Mbandaka",
     "Un pisciculteur de Mbandaka met 200 alevins dans un étang. La population double tous les 3 mois tant que la nourriture suffit. Il veut savoir au bout de combien de temps il atteindra 3 200 poissons pour prévoir la récolte. Après combien de mois la population atteint-elle 3 200 poissons ?",
     ["9 mois", "12 mois", "15 mois", "16 mois", "48 mois"], 2,
     "3 200 / 200 = 16 = 2^4 : il faut 4 doublements, soit 4 × 3 = 12 mois. Par le logarithme : n = log(16)/log(2) = 4.",
     "1 : 3 doublements ; 3 : 5 doublements ; 4 : facteur 16 pris pour des mois ; 5 : 16 × 3"),
    ("Mathématiques", None, "Statistiques", "moyen",
     "Notes d'un contrôle de mathématiques à Kisangani",
     "Un professeur de Kisangani relève les notes sur 10 de cinq élèves à un contrôle : 4, 6, 7, 8 et 10. Il veut communiquer aux parents la note moyenne de ce groupe. Quelle est la moyenne de ces cinq notes ?",
     ["6", "7", "7,5", "35", "8"], 2,
     "Moyenne = (4 + 6 + 7 + 8 + 10) / 5 = 35 / 5 = 7.",
     "1 : médiane des quatre premières ; 3 : (4+10)/2 + ... erreur ; 4 : somme non divisée ; 5 : division par 4"),
    # ---------------- SVT (4, partiel)
    ("SVT", "Biologie", "Immunologie et groupes sanguins", "difficile",
     "Transfusion dans un centre de santé de Goma",
     "Dans un centre de santé de Goma, un blessé de groupe sanguin O rhésus négatif doit être transfusé d'urgence. L'infirmier dispose de poches A+, B-, AB+, O+ et O-. Quelle poche peut-il utiliser sans risque d'agglutination ?",
     ["A+", "B-", "AB+", "O+", "O-"], 5,
     "Un receveur O- n'a aucun antigène A, B ni D sur ses hématies et possède les anticorps anti-A et anti-B ; seul le sang O- n'apporte aucun antigène étranger.",
     "4 : rhésus ignoré ; 1 et 2 : un antigène ABO présent ; 3 : confusion avec le receveur universel"),
    ("SVT", "Biologie", "Génétique et hérédité", "moyen",
     "Croisement de plants de maïs dans une ferme-école de Kikwit",
     "Dans une ferme-école de Kikwit, on croise deux plants de maïs hétérozygotes (Aa × Aa) pour un caractère à dominance complète. Les élèves comptent les grains de phénotype récessif pour vérifier la loi de Mendel. Quelle proportion de descendants présente le phénotype récessif ?",
     ["0 %", "25 %", "50 %", "75 %", "100 %"], 2,
     "Échiquier de croisement : AA, Aa, Aa, aa. Le phénotype récessif correspond au seul génotype aa, soit 1/4 = 25 %.",
     "3 : proportion des hétérozygotes ; 4 : phénotype dominant ; 1 et 5 : confusion dominance/récessivité"),
    ("SVT", "Écologie", "Écosystèmes et chaînes alimentaires", "facile",
     "Chaîne alimentaire dans une savane du Katanga",
     "Dans une savane du Katanga, des élèves observent que l'herbe est broutée par des antilopes, elles-mêmes chassées par des lions. Ils doivent classer chaque être vivant selon son rôle dans la chaîne alimentaire. Quel est le rôle de l'antilope dans cette chaîne ?",
     ["producteur", "consommateur primaire", "consommateur secondaire", "décomposeur", "prédateur final"], 2,
     "L'herbe est le producteur ; l'antilope, herbivore, est le consommateur primaire ; le lion, carnivore, est le consommateur secondaire.",
     "1 : rôle de l'herbe ; 3 et 5 : rôle du lion ; 4 : rôle des bactéries et champignons"),
    ("SVT", "Géologie & Évolution", "Structure de la Terre et roches", "facile",
     "Roche volcanique ramassée près du Nyiragongo",
     "Près de Goma, un élève ramasse une roche noire, légère, pleine de petites cavités, provenant d'une coulée du volcan Nyiragongo. Il doit l'identifier pour son herbier géologique. À quelle famille de roches appartient-elle ?",
     ["roche sédimentaire", "roche magmatique volcanique", "roche métamorphique", "roche magmatique plutonique", "fossile"], 2,
     "Une roche issue d'une coulée de lave refroidie rapidement en surface, avec des bulles de gaz figées, est une roche magmatique volcanique (basalte).",
     "1 : formée par dépôt ; 3 : transformée par pression/chaleur ; 4 : refroidie en profondeur (granite) ; 5 : reste d'être vivant"),
]


def charger_demo() -> int:
    with connect() as con:
        con.execute("DELETE FROM items WHERE version='demo'")
        for k, (d, sd, ch, diff, titre, tige, props, rep, corr, err) in enumerate(ITEMS, 1):
            con.execute(
                """INSERT INTO items(id, option_code, epreuve_code, discipline, sous_discipline, chapitre, savoir_essentiel, competence,
                   difficulte, famille_contexte, titre, tige, p1,p2,p3,p4,p5, reponse, correction_detaillee,
                   erreurs_distracteurs, nb_mots_tige, version, statut_validation, validateur, date_validation)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'demo','valide','demo',?)""",
                (f"DEMO-{k:03d}", "1.02", EPREUVE_PAR_DISCIPLINE_V1.get(d), d, sd, ch, ch, "calculer", diff, "quotidien", titre, tige, *props, rep,
                 corr, err, compter_mots(tige), maintenant()),
            )
        return len(ITEMS)


SITUATION_DEMO = {
    "situation": {
        "titre": "Kit solaire pour le centre de santé de Kikwit",
        "chapitres": "Électricité : puissance et énergie ; Énergie solaire et stockage",
        "duree_min": 25,
        "texte": (
            "Le centre de santé de référence de Kikwit, dans le Kwilu, fonctionne avec un groupe électrogène qui consomme "
            "chaque mois pour 420 000 FC de carburant et tombe souvent en panne. Le médecin-chef étudie une offre de kit "
            "solaire proposée par un fournisseur de Kinshasa : 3 panneaux de 330 Wc, 1 batterie de 12 V – 200 Ah et un "
            "onduleur. Il relève la liste des appareils indispensables et leur durée d'utilisation quotidienne (document 1). "
            "Le fournisseur précise que l'ensoleillement moyen à Kikwit permet 5 heures d'équivalent plein soleil par jour, "
            "que le rendement global de l'installation (câbles, régulateur, onduleur) est de 0,8 et que la batterie ne doit "
            "jamais être déchargée au-delà de 50 % de sa capacité pour durer. La nuit, de 18 h à 6 h, seuls le "
            "réfrigérateur à vaccins et les lampes restent en service : le réfrigérateur toute la nuit, les lampes pendant "
            "6 heures. Le médecin-chef veut savoir si le kit proposé couvre les besoins du centre et, sinon, ce qu'il faut "
            "modifier avant de signer."
        ),
        "document_texte": (
            "Document 1 — Appareils du centre : 10 lampes LED de 10 W utilisées 12 h/jour ; 1 réfrigérateur à vaccins de "
            "60 W utilisé 24 h/jour ; 1 stérilisateur de 500 W utilisé 2 h/jour ; 2 ventilateurs de 50 W utilisés 8 h/jour ; "
            "1 microscope avec ordinateur de 100 W utilisé 6 h/jour. Document 2 — Kit proposé : 3 panneaux de 330 Wc ; "
            "1 batterie 12 V – 200 Ah ; ensoleillement 5 h/jour ; rendement global 0,8 ; décharge maximale 50 %."
        ),
        "document_latex": (
            "\\begin{tabular}{lccc}\\toprule Appareil & Nombre & Puissance unitaire & Durée par jour\\\\\\midrule "
            "Lampe LED & 10 & 10 W & 12 h\\\\ Réfrigérateur à vaccins & 1 & 60 W & 24 h\\\\ Stérilisateur & 1 & 500 W & 2 h\\\\ "
            "Ventilateur & 2 & 50 W & 8 h\\\\ Microscope + ordinateur & 1 & 100 W & 6 h\\\\\\bottomrule\\end{tabular}"
        ),
        "synthese": (
            "Les appareils du centre demandent 5,04 kWh par jour. Un panneau de 330 Wc fournit 330 × 5 × 0,8 = 1 320 Wh par "
            "jour : il faut 4 panneaux, pas 3. La batterie n'offre que 1 200 Wh utilisables alors que la nuit exige "
            "720 + 600 = 1 320 Wh : une seconde batterie est nécessaire. Le kit proposé est donc insuffisant ; il faut le "
            "porter à 4 panneaux et 2 batteries avant de signer."
        ),
    },
    "items": [
        ("facile", "Électricité : puissance et énergie", "Q1 — Puissance totale des appareils",
         "D'après le document 1, quelle est la puissance totale des appareils du centre lorsqu'ils fonctionnent tous en même temps ?",
         ["760 W", "860 W", "720 W", "1 060 W", "5 040 W"], 2,
         "P = 10 × 10 + 60 + 500 + 2 × 50 + 100 = 100 + 60 + 500 + 100 + 100 = 860 W.",
         "1 : ventilateurs comptés une fois ; 3 : lampes et ventilateurs mal multipliés ; 4 : lampes comptées 20 ; 5 : énergie journalière en Wh confondue avec une puissance"),
        ("moyen", "Électricité : puissance et énergie", "Q2 — Énergie consommée par jour",
         "Quelle énergie électrique les appareils du centre consomment-ils en une journée ?",
         ["0,86 kWh", "5,04 kWh", "20,6 kWh", "50,4 kWh", "4,44 kWh"], 2,
         "E = Σ P × t = 100 × 12 + 60 × 24 + 500 × 2 + 100 × 8 + 100 × 6 = 1 200 + 1 440 + 1 000 + 800 + 600 = 5 040 Wh = 5,04 kWh.",
         "1 : puissance recopiée ; 3 : 860 W × 24 h ; 4 : erreur de puissance de dix ; 5 : stérilisateur oublié"),
        ("moyen", "Énergie solaire et stockage", "Q3 — Nombre de panneaux nécessaires",
         "On admet que le centre consomme 5,04 kWh par jour. Avec 5 h d'ensoleillement et un rendement global de 0,8, combien de panneaux de 330 Wc faut-il au minimum ?",
         ["1", "2", "3", "4", "15"], 4,
         "Production journalière d'un panneau : 330 × 5 × 0,8 = 1 320 Wh. Nombre : 5 040 / 1 320 = 3,8, donc 4 panneaux (on arrondit toujours au-dessus).",
         "1 et 2 : erreurs de division ; 3 : arrondi au-dessous ; 5 : 5 040 / 330 sans tenir compte des heures d'ensoleillement"),
        ("difficile", "Énergie solaire et stockage", "Q4 — Énergie utilisable de la batterie",
         "Quelle énergie la batterie de 12 V – 200 Ah peut-elle réellement fournir chaque nuit si l'on respecte la décharge maximale de 50 % ?",
         ["2 400 Wh", "200 Wh", "1 200 Wh", "100 Wh", "600 Wh"], 3,
         "Capacité totale : E = U × Q = 12 × 200 = 2 400 Wh. Avec une décharge limitée à 50 % : 2 400 × 0,5 = 1 200 Wh utilisables.",
         "1 : limite de décharge oubliée ; 2 : Ah confondus avec Wh ; 4 : moitié des Ah ; 5 : décharge à 25 %"),
        ("difficile", "Énergie solaire et stockage", "Q5 — Décision du médecin-chef",
         "On admet qu'une batterie fournit 1 200 Wh utilisables par nuit. La nuit, le réfrigérateur (60 W, 12 h) et les lampes (100 W, 6 h) restent en service. Que doit décider le médecin-chef ?",
         ["Signer : le kit de 3 panneaux et 1 batterie suffit", "Passer à 4 panneaux ; 1 batterie suffit", "Passer à 4 panneaux et 2 batteries",
          "Garder 3 panneaux mais prendre 2 batteries", "Renoncer au solaire et garder le groupe électrogène"], 3,
         "Besoin nocturne : 60 × 12 + 100 × 6 = 720 + 600 = 1 320 Wh, supérieur aux 1 200 Wh utilisables d'une batterie : il faut 2 batteries. Et la Q3 a montré qu'il faut 4 panneaux pour produire les 5,04 kWh journaliers. Le kit doit donc être porté à 4 panneaux et 2 batteries.",
         "1 : aucune vérification ; 2 : besoin nocturne non calculé ; 4 : production journalière ignorée ; 5 : conclusion sans rapport avec les calculs"),
    ],
}


def charger_situation_demo() -> str:
    from .situations import inserer_situation

    with connect() as con:
        con.execute("DELETE FROM items WHERE situation_id IN (SELECT id FROM situations WHERE version='demo')")
        con.execute("DELETE FROM situations WHERE version='demo'")
        items = [{"ordre": k, "discipline": "Physique", "chapitre": ch, "savoir_essentiel": ch, "competence": "calculer",
                  "difficulte": d, "famille_contexte": "santé / énergie", "support": "aucun", "titre": t, "tige": tige,
                  "propositions": props, "reponse": r, "correction_detaillee": corr, "erreurs_distracteurs": err}
                 for k, (d, ch, t, tige, props, r, corr, err) in enumerate(SITUATION_DEMO["items"], 1)]
        sid = inserer_situation(con, {"situation": SITUATION_DEMO["situation"], "items": items},
                                discipline="Physique", sous_discipline=None, modele="demo", epreuve_code="M.07")
        con.execute("UPDATE situations SET version='demo', statut_validation='valide', validateur='demo', "
                    "date_validation=?, observations=NULL WHERE id=?", (maintenant(), sid))
        con.execute("UPDATE items SET version='demo', statut_validation='valide', validateur='demo', "
                    "date_validation=?, observations=NULL WHERE situation_id=?", (maintenant(), sid))
        return sid
