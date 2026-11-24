"""Lot 1 — option 1.02 Sciences : 40 items avec figure (Mathématiques 15, Physique 10, Chimie 7, SVT 8).

Chaque item suit la charte (micro-contexte 35–75 mots, 5 propositions, une seule bonne réponse, distracteurs = erreurs
d'élèves, correction détaillée) ; la figure est nécessaire à la résolution (au moins une donnée n'est lisible que sur elle).
Les valeurs numériques sont calculées ici-même pour éviter toute erreur de clé.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from figures import (NUIT, OR, ROUGE, VERT, GRIS, Plot, cases_quantiques, chariots, chromatogramme, circuit_serie, corde, cycle_pv,  # noqa: E402
                     fmt, frise, lentille, montage_titrage, pave, pedigree, pie, pile, plan_incline, punnett, reseau_trophique, table,
                     transformateur, tree)

ITEMS: list[dict] = []
CH = {  # chapitres exacts du programme chargé
    "cplx": "Nombres complexes : construction, représentations, équations (MM6.1–6.3)",
    "logexp": "Fonctions logarithmiques et exponentielles : étude, dérivées (MM6.4–6.5)",
    "eqlog": "Équations, inéquations et applications log-exp (MM6.6–6.8)",
    "serie": "Développement en série des fonctions usuelles (MM6.9)",
    "integ": "Différentielle, primitives, intégration (MM6.10–6.12)",
    "appint": "Applications géométriques de l'intégrale (MM6.13)",
    "proba": "Probabilités (MM6.14)",
    "stat": "Statistiques : paramètres de dispersion, lois de distribution (MM6.15–6.16)",
    "coniq": "Lieux géométriques et coniques : éléments focaux, tangentes, asymptotes, sommets (MM6.17–6.23)",
    "simil": "Similitudes planes (MM6.24)",
    "espace": "Géométrie de l'espace : plans, droites, rabattement, relèvement, rotations (MM6.25–6.31)",
    "cine": "Cinématique : MRU, MRUV, chute libre, mouvements circulaires (MSP6.1–6.5)",
    "dyn": "Dynamique : lois de Newton, balistique, force centripète, moments d'inertie (MSP6.6–6.9)",
    "poids": "Poids et attraction universelle, frottements, ascenseurs, plan incliné, résistance de l'air (MSP6.10–6.14)",
    "energie": "Énergie mécanique, quantité de mouvement, moment cinétique, volant, marteau (MSP6.15–6.19)",
    "thermo": "Thermodynamique et moteurs à combustion interne (MSP6.20–6.21)",
    "oscil": "Oscillateurs et pendules (MSP6.22–6.28)",
    "ondes": "Ondes : électromagnétiques, interférences, ondes stationnaires, acoustique, effet Doppler (MSP6.29–6.35)",
    "alternatif": "Courant alternatif : lois d'Ohm, circuits RLC, puissance et transformateur (MSP6.36–6.38)",
    "solutions": "Solutions : concentration, préparation d'une solution titrée (MSPC6.1)",
    "labo": "Laboratoire : matériel et sécurité (MSPC6.2–6.3)",
    "titrage": "Titrages volumétriques : acido-basique, précipitation, oxydoréduction (MSPC6.4–6.6)",
    "electrochimie": "Électrochimie : potentiel redox, pile (MSPC6.7)",
    "atome": "Atome : constituants, modèles, nombres quantiques, structure électronique (MSPC6.8–6.9)",
    "noyau": "Noyau atomique : radioactivité, énergie nucléaire, radio-isotopes (MSPC6.10–6.12)",
    "separation": "Séparation et identification : chromatographie, cations, anions (MSPC6.13–6.15)",
    "cyto": "Cytologie : cycle cellulaire, anomalies chromosomiques (MSVT6.1–6.2)",
    "repro": "Reproduction humaine : cycle menstruel, fécondation (MSVT6.3–6.5)",
    "immuno": "Immunologie : système immunitaire, dysfonctionnements, aides à la réponse (MSVT6.6–6.8)",
    "genet": "Génétique : mono- et dihybridisme, interactions géniques (MSVT6.9–6.13)",
    "genhum": "Génétique humaine : hérédité liée au sexe et autosomale (MSVT6.14–6.15)",
    "khi": "Hérédité et probabilités, test du khi-carré, théorie chromosomique (MSVT6.16–6.20)",
    "geol": "Chronologie géologique (MSVT6.22)",
    "ecosys": "Écosystèmes : interdépendance, limites, dynamique (MSVT6.26–6.29)",
    "ecoconcepts": "Concepts écologiques, adaptabilité, écologie et autres sciences (MSVT6.23–6.25)",
}


def item(num: str, discipline: str, sd, chapitre: str, difficulte: str, competence: str, savoir: str, famille: str, titre: str,
         tige: str, props: list, reponse: int, correction: str, erreurs: str, fig: str, legende: str) -> None:
    assert len(props) == 5 and 1 <= reponse <= 5, titre
    assert len(set(map(str, props))) == 5, f"propositions non distinctes : {titre}"
    nb = len(tige.split())
    assert 30 <= nb <= 95, f"{titre} : {nb} mots"
    assert fig.lstrip().startswith("<svg") and "<script" not in fig
    ITEMS.append({
        "id": f"FIG1-{num}", "discipline": discipline, "sous_discipline": sd, "epreuve_code": "M.07" if discipline in ("Physique", "Chimie") else "M.46",
        "chapitre": CH[chapitre], "savoir_essentiel": savoir, "competence": competence, "difficulte": difficulte, "famille_contexte": famille,
        "support": "figure", "titre": titre, "tige": tige, "propositions": [str(p) for p in props], "reponse": reponse,
        "correction_detaillee": correction, "erreurs_distracteurs": erreurs, "nb_mots_tige": nb,
        "figure_svg": fig, "figure_legende": legende,
    })


# =====================================================================================================================
# MATHÉMATIQUES (15)
# =====================================================================================================================

# M01 — exponentielle : lecture d'un zéro ------------------------------------------------------------------------------
p = Plot(-2, 3, -3, 6, xstep=1, ystep=1)
p.curve(lambda x: math.exp(x) - 2)
p.point(0, -1, "A(0 ; −1)", dx=10, dy=14)
p.label(2.1, 4.6, "C", NUIT, 14, weight="bold")
item("M01", "Mathématiques", None, "logexp", "facile", "interpréter", "Zéro d'une fonction exponentielle, résolution de e^x = k", "document graphique",
     "Courbe d'une notice technique",
     "Le graphique ci-contre, tiré d'une notice technique, représente la courbe C d'une fonction f définie sur ℝ par f(x) = eˣ − 2. "
     "La courbe passe par le point A(0 ; −1) et coupe l'axe des abscisses en un point dont on cherche l'abscisse exacte. "
     "Quelle est cette abscisse ?",
     ["ln 2", "e²", "2", "ln(−2)", "1/2"], 1,
     "On résout f(x) = 0 : eˣ − 2 = 0 ⇔ eˣ = 2 ⇔ x = ln 2 ≈ 0,69, ce qui est cohérent avec la lecture graphique (entre 0 et 1). "
     "Vérification : f(0) = e⁰ − 2 = −1, le point A est bien sur la courbe.",
     "2 : confusion entre eˣ = 2 et x = e² ; 3 : lecture de la valeur 2 au lieu de résoudre ; 4 : ln(−2) n'existe pas ; 5 : lecture approximative erronée.",
     p.render(), "Courbe C de la fonction f(x) = eˣ − 2 dans un repère orthonormé")

# M02 — logarithme : aire sous la courbe --------------------------------------------------------------------------------
p = Plot(0, 4, -1.5, 2, xstep=1, ystep=0.5, yfmt=lambda v: fmt(v))
p.area(math.log, 1, math.e)
p.curve(math.log, 0.05, 4)
p.dashes_to_axes(math.e, 1)
p.label(math.e, -0.28, "e", ROUGE, 13, "middle", "bold")
p.label(2.15, 0.3, "D", OR, 16, weight="bold")
item("M02", "Mathématiques", None, "integ", "moyen", "calculer", "Intégration par parties : primitive de ln x, calcul d'aire", "document graphique",
     "Surface d'une pièce de tôle",
     "Un ferblantier découpe une pièce dont le profil est donné par la courbe de la fonction ln sur un plan à l'échelle 1 unité = 1 dm. "
     "Le domaine D, coloré sur le graphique, est limité par la courbe, l'axe des abscisses et les droites x = 1 et x = e. "
     "Quelle est l'aire exacte de D, en dm² ?",
     ["1", "e − 1", "e", "ln 2", "e/2"], 1,
     "Aire de D = ∫₁ᵉ ln x dx. Une primitive de ln x est x ln x − x (intégration par parties : u = ln x, dv = dx). "
     "Donc ∫₁ᵉ ln x dx = [x ln x − x]₁ᵉ = (e·1 − e) − (1·0 − 1) = 0 + 1 = 1 dm².",
     "2 : confusion avec ∫₀¹ eˣ dx ; 3 : prise de la borne supérieure pour l'aire ; 4 : différence ln e − ln 1 mal calculée ; 5 : estimation grossière (moitié d'un rectangle).",
     p.render(), "Domaine D sous la courbe de ln entre x = 1 et x = e")

# M03 — tangente : pente ----------------------------------------------------------------------------------------------
p = Plot(-1, 3, -2, 6, xstep=1, ystep=1)
p.curve(lambda x: x * x)
p.segment(-0.5, -2, 2.5, 4, ROUGE, 1.8)  # tangente en x=1 : y = 2x - 1
p.point(1, 1, "T(1 ; 1)", dx=-10, dy=-10, anchor="end")
p.label(2.3, 4.7, "tangente", ROUGE, 12, "start", italic=True)
item("M03", "Mathématiques", None, "integ", "facile", "interpréter", "Nombre dérivé et coefficient directeur de la tangente", "document graphique",
     "Pente d'une rampe sur un plan",
     "Sur le plan d'une rampe d'accès, un dessinateur a tracé la courbe d'équation y = x² et, en rouge, la tangente à cette courbe au point T d'abscisse 1. "
     "Il doit indiquer la pente de cette tangente, c'est-à-dire son coefficient directeur. Quelle valeur doit-il inscrire ?",
     ["2", "1", "0,5", "4", "−1"], 1,
     "Le coefficient directeur de la tangente en x = 1 est le nombre dérivé f′(1). Avec f(x) = x², f′(x) = 2x, donc f′(1) = 2. "
     "Lecture sur la figure : la tangente passe par (1 ; 1) et (2 ; 3) : pente (3 − 1)/(2 − 1) = 2.",
     "2 : confusion avec l'ordonnée du point T ; 3 : inversion du quotient ; 4 : calcul de f(2) au lieu de f′(1) ; 5 : signe lu à l'envers.",
     p.render(), "Courbe y = x² et sa tangente au point T")

# M04 — volume de révolution --------------------------------------------------------------------------------------------
p = Plot(0, 5, -2.5, 2.5, xstep=1, ystep=1)
p.area(math.sqrt, 0, 4)
p.curve(math.sqrt, 0, 4.6)
p.curve(lambda x: -math.sqrt(x), 0, 4.6, color=GRIS, dash="5 4")
p.segment(4, -2, 4, 2, NUIT, 1.2, dash="4 3")
p.label(4.05, -2.35, "x = 4", NUIT, 12, "start")
p.label(2.2, 1.9, "y = √x", NUIT, 13, "start", italic=True)
item("M04", "Mathématiques", None, "appint", "difficile", "modéliser", "Volume d'un solide de révolution : V = π∫f(x)² dx", "objet technique",
     "Volume d'un entonnoir tourné",
     "Un tourneur sur bois fabrique une pièce en faisant tourner autour de l'axe des abscisses la région comprise entre la courbe y = √x, "
     "l'axe des abscisses et la droite x = 4 (unité : 1 dm). La figure montre la région et, en pointillés, sa symétrique. "
     "Quel est le volume de la pièce, en dm³ ?",
     ["8π", "16π/3", "4π", "16π", "64π/3"], 1,
     "V = π∫₀⁴ (√x)² dx = π∫₀⁴ x dx = π[x²/2]₀⁴ = π × 16/2 = 8π ≈ 25,1 dm³.",
     "2 : calcul de π∫₀⁴ √x dx (oubli du carré) donne 16π/3 ; 3 : confusion avec l'aire 2·∫√x ; 4 : oubli de la division par 2 dans la primitive de x ; 5 : intégration de x² au lieu de x.",
     p.render(), "Région limitée par y = √x, l'axe (Ox) et x = 4, tournant autour de (Ox)")

# M05 — arbre de probabilités --------------------------------------------------------------------------------------------
fig = tree([("Réseau A", "0,6", [("Appel réussi", "0,9"), ("Appel échoué", "0,1")]), ("Réseau B", "0,4", [("Appel réussi", "0,75"), ("Appel échoué", "0,25")])])
pA = 0.6 * 0.9 + 0.4 * 0.75
item("M05", "Mathématiques", None, "proba", "moyen", "calculer", "Probabilités conditionnelles, formule des probabilités totales", "document technique",
     "Fiabilité des appels d'une radio communautaire",
     "Une radio communautaire relaie ses reportages par téléphone. L'arbre pondéré ci-contre, dressé par le technicien, donne la probabilité qu'un appel passe par le réseau A ou B, "
     "puis qu'il réussisse. Un appel est choisi au hasard. Quelle est la probabilité qu'il réussisse ?",
     ["0,84", "0,54", "0,825", "1,65", "0,30"], 1,
     f"Formule des probabilités totales : P(réussi) = P(A)·P(réussi|A) + P(B)·P(réussi|B) = 0,6 × 0,9 + 0,4 × 0,75 = 0,54 + 0,30 = {pA:.2f}.".replace(".", ","),
     "2 : seule la branche A est prise en compte ; 3 : moyenne simple des deux probabilités conditionnelles (0,9 + 0,75)/2 ; 4 : somme des conditionnelles sans pondération ; 5 : seule la branche B.",
     fig, "Arbre pondéré : réseau utilisé puis issue de l'appel")

# M06 — diagramme en bâtons : moyenne ----------------------------------------------------------------------------------
data = [(0, 1), (1, 3), (2, 6), (3, 5), (4, 3), (5, 2)]
N = sum(n for _, n in data)
moy = sum(x * n for x, n in data) / N
p = Plot(0.3, 6.9, 0, 7, 420, 280, xstep=1, ystep=1, xlabel="pannes par mois", ylabel="effectif", grid=False, xfmt=lambda v: fmt(v - 1))
p.bars([(x + 1, n) for x, n in data], 0.55)
item("M06", "Mathématiques", None, "stat", "facile", "calculer", "Moyenne d'une série statistique à partir d'un diagramme en bâtons", "donnée brute",
     "Pannes mensuelles d'un moulin à maïs",
     "Le carnet d'entretien d'un moulin à maïs recense, sur vingt mois, le nombre de pannes survenues chaque mois. "
     "Le diagramme en bâtons ci-contre en donne la distribution : par exemple, six mois ont connu exactement deux pannes. "
     "Quel est le nombre moyen de pannes par mois ?",
     [fmt(round(moy, 2)), "2,5", "3", "2", "3,33"], 1,
     f"Effectif total N = 1+3+6+5+3+2 = {N}. Somme des pannes = 0·1 + 1·3 + 2·6 + 3·5 + 4·3 + 5·2 = 0+3+12+15+12+10 = {sum(x * n for x, n in data)}. "
     f"Moyenne = {sum(x * n for x, n in data)}/{N} = {moy:.2f}.".replace(".", ","),
     "2 : moyenne des valeurs 0 à 5 sans pondération par les effectifs ; 3 : valeur du bâton le plus haut confondue avec le mode décalé ; 4 : mode pris pour la moyenne ; 5 : division par 6 (nombre de valeurs) au lieu de 20.",
     p.render(), "Nombre de mois (effectif) selon le nombre de pannes")

# M07 — tableau : écart-type ----------------------------------------------------------------------------------------------
vals = [(10, 2), (12, 5), (14, 8), (16, 4), (18, 1)]
N7 = sum(n for _, n in vals)
m7 = sum(x * n for x, n in vals) / N7
var7 = sum(n * (x - m7) ** 2 for x, n in vals) / N7
et7 = math.sqrt(var7)
fig = table(["Masse (kg)", "10", "12", "14", "16", "18"], [["Nombre de sacs", "2", "5", "8", "4", "1"]], col_w=[120, 60, 60, 60, 60, 60], first_col_bold=True)
item("M07", "Mathématiques", None, "stat", "difficile", "calculer", "Variance et écart-type d'une série pondérée", "donnée brute",
     "Régularité du remplissage de sacs de charbon",
     "Un contrôleur pèse vingt sacs de charbon de bois à la sortie d'une carbonisation ; les masses obtenues sont rassemblées dans le tableau ci-contre. "
     "Pour juger de la régularité du remplissage, il calcule l'écart-type de la série. Quelle valeur, arrondie au centième, obtient-il ?",
     [fmt(round(et7, 2)), fmt(round(var7, 2)), "2,83", "2", "1,60"], 1,
     f"Moyenne : (10·2 + 12·5 + 14·8 + 16·4 + 18·1)/20 = {sum(x * n for x, n in vals)}/20 = {m7:.1f} kg. "
     f"Variance : Σnᵢ(xᵢ − x̄)²/N = [2·(−3,6)² + 5·(−1,6)² + 8·(0,4)² + 4·(2,4)² + 1·(4,4)²]/20 = {var7:.2f}. "
     f"Écart-type = √{var7:.2f} ≈ {et7:.2f} kg.".replace(".", ","),
     "2 : variance donnée à la place de l'écart-type ; 3 : écart-type des cinq valeurs 10…18 sans pondération ; 4 : pas du tableau pris pour l'écart-type ; 5 : écart moyen absolu confondu avec l'écart-type.",
     fig, "Répartition des masses de vingt sacs")

# M08 — complexes : module -------------------------------------------------------------------------------------------------
p = Plot(-1, 5, -1, 5, 360, 320, xstep=1, ystep=1, xlabel="Re", ylabel="Im")
p.segment(0, 0, 3, 4, NUIT, 2, arrow=True)
p.dashes_to_axes(3, 4)
p.point(3, 4, "M", dx=8, dy=-6)
item("M08", "Mathématiques", None, "cplx", "facile", "calculer", "Module d'un nombre complexe à partir de son image", "document graphique",
     "Portée d'une antenne sur un plan quadrillé",
     "Sur le plan quadrillé d'un installateur, l'antenne est à l'origine O et une maison au point M, image du nombre complexe z (1 unité = 100 m). "
     "La figure permet de lire les coordonnées de M. Quelle est la distance OM, c'est-à-dire le module de z, en mètres ?",
     ["500", "700", "340", "250", "120"], 1,
     "Lecture : M(3 ; 4), donc z = 3 + 4i. |z| = √(3² + 4²) = √25 = 5 unités, soit 5 × 100 = 500 m.",
     "2 : somme 3 + 4 = 7 prise pour le module ; 3 : coordonnées juxtaposées ; 4 : 25 sans la racine, divisé par l'échelle ; 5 : produit 3 × 4.",
     p.render(), "Image M du nombre complexe z dans le plan complexe")

# M09 — complexes : multiplication par i = rotation ------------------------------------------------------------------------
p = Plot(-4, 4, -4, 4, 360, 340, xstep=1, ystep=1, xlabel="Re", ylabel="Im")
pts = {"A": (3, 1), "B": (-1, 3), "C": (-3, -1), "D": (1, -3), "E": (3, -1)}
for k, (x, y) in pts.items():
    p.point(x, y, k, dx=8, dy=-6)
p.segment(0, 0, 3, 1, NUIT, 1.6, arrow=True)
item("M09", "Mathématiques", None, "cplx", "moyen", "raisonner", "Interprétation géométrique de la multiplication par i (rotation d'angle π/2)", "document graphique",
     "Rotation d'un bras de grue",
     "Sur le schéma de commande d'une grue portuaire, l'extrémité du bras est au point A d'affixe z_A = 3 + i. Le bras tourne d'un quart de tour dans le sens direct autour de O. "
     "Parmi les points B, C, D, E placés sur la figure, lequel est l'image de A, c'est-à-dire le point d'affixe i·z_A ?",
     ["B", "C", "D", "E", "aucun de ces points"], 1,
     "i·z_A = i(3 + i) = 3i + i² = −1 + 3i : c'est le point B(−1 ; 3). Géométriquement, multiplier par i revient à tourner de +π/2 autour de O, et OB est bien perpendiculaire à OA, de même longueur √10.",
     "2 : C correspond à −z_A (rotation d'un demi-tour) ; 3 : D correspond à −i·z_A (quart de tour indirect) ; 4 : E est le conjugué de A ; 5 : réponse par abandon.",
     p.render(), "Point A et quatre points candidats dans le plan complexe")

# M10 — parabole : foyer -------------------------------------------------------------------------------------------------------
p = Plot(-3, 6, -5, 5, 420, 320, xstep=1, ystep=1)
p.curve(lambda x: 2 * math.sqrt(x), 0, 6)
p.curve(lambda x: -2 * math.sqrt(x), 0, 6)
p.segment(-1, -5, -1, 5, ROUGE, 1.6, dash="6 4")
p.label(-1, 4.6, "(d)", ROUGE, 13, "end", "bold")
p.point(1, 0, "F", ROUGE, dx=6, dy=16)
p.point(0, 0, "S", dx=-8, dy=-8, anchor="end")
item("M10", "Mathématiques", None, "coniq", "moyen", "interpréter", "Parabole : foyer, directrice, paramètre", "objet technique",
     "Réflecteur parabolique d'un four solaire",
     "La coupe d'un four solaire artisanal est une parabole de sommet S, tracée ci-contre dans un repère où l'unité vaut 10 cm. "
     "La droite (d) est sa directrice et F son foyer, point où l'on place la marmite. Quelle est l'équation de cette parabole ?",
     ["y² = 4x", "y² = 2x", "y² = x", "x² = 4y", "y² = 8x"], 1,
     "Le foyer F(1 ; 0) et la directrice x = −1 donnent p/2 = 1, soit p = 2 : la parabole d'axe (Ox) et de sommet O a pour équation y² = 2px = 4x. "
     "Vérification : le point (1 ; 2) de la courbe satisfait 2² = 4 × 1.",
     "2 : confusion entre p et 2p ; 3 : p/2 pris pour 2p ; 4 : axe de symétrie inversé ; 5 : distance FH = 2 prise pour p/2.",
     p.render(), "Parabole de sommet S, foyer F et directrice (d)")

# M11 — ellipse : excentricité -----------------------------------------------------------------------------------------------
p = Plot(-6, 6, -4, 4, 460, 300, xstep=1, ystep=1)
p.curve(lambda x: 3 * math.sqrt(max(0, 1 - x * x / 25)), -5, 5)
p.curve(lambda x: -3 * math.sqrt(max(0, 1 - x * x / 25)), -5, 5)
p.point(5, 0, "A", dx=6, dy=16); p.point(-5, 0, "A'", dx=-6, dy=16, anchor="end"); p.point(0, 3, "B", dx=8, dy=-6); p.point(0, -3, "B'", dx=8, dy=14)
item("M11", "Mathématiques", None, "coniq", "difficile", "calculer", "Ellipse : demi-axes, distance focale, excentricité", "objet technique",
     "Orbite d'un satellite sur un schéma",
     "Un schéma pédagogique du musée des sciences représente l'orbite elliptique d'un satellite dans un repère centré sur le centre de l'ellipse : "
     "les sommets A, A', B, B' sont marqués. Le centre de la Terre occupe l'un des foyers. Quelle est l'excentricité de cette orbite ?",
     ["0,8", "0,6", "1,25", "4", "0,36"], 1,
     "Lecture : a = OA = 5 et b = OB = 3. Distance focale c = √(a² − b²) = √(25 − 9) = √16 = 4. Excentricité e = c/a = 4/5 = 0,8.",
     "2 : b/a au lieu de c/a ; 3 : a/c, rapport inversé ; 4 : c donné à la place de e ; 5 : (b/a)².",
     p.render(), "Ellipse de sommets A, A', B, B'")

# M12 — similitude : rapport et aires ----------------------------------------------------------------------------------------
p = Plot(-1, 9, -1, 7, 440, 320, xstep=1, ystep=1, grid=True)
p.polyline([(0, 0), (2, 0), (0, 1.5)], NUIT, 2.2, close=True, fill="#F7F4EC")
p.polyline([(3, 1), (7, 1), (3, 4)], ROUGE, 2.2, close=True, fill="#FBEFEF")
for k, (x, y) in {"A": (0, 0), "B": (2, 0), "C": (0, 1.5)}.items():
    p.label(x + (0.1 if k != "C" else 0.15), y + (-0.3 if k != "C" else 0.35), k, NUIT, 13, weight="bold")
for k, (x, y) in {"A'": (3, 1), "B'": (7, 1), "C'": (3, 4)}.items():
    p.label(x + (0.1 if k != "C'" else -0.5), y + (-0.3 if k != "C'" else 0.3), k, ROUGE, 13, weight="bold")
item("M12", "Mathématiques", None, "simil", "moyen", "raisonner", "Similitude plane : rapport k, effet sur les longueurs et les aires", "document graphique",
     "Agrandissement d'un patron de couture",
     "Une couturière agrandit un patron triangulaire ABC pour obtenir A'B'C', comme le montre le quadrillage (1 carreau = 1 dm). "
     "Les deux triangles sont semblables, A'B'C' étant l'image de ABC par une similitude directe. Combien de fois l'aire de A'B'C' est-elle plus grande que celle de ABC ?",
     ["4", "2", "8", "6", "2,5"], 1,
     "Rapport de la similitude : k = A'B'/AB = 4/2 = 2 (on vérifie A'C'/AC = 3/1,5 = 2). Une similitude de rapport k multiplie les aires par k² = 4. "
     "Contrôle direct : aire(ABC) = 2 × 1,5/2 = 1,5 dm² ; aire(A'B'C') = 4 × 3/2 = 6 dm² ; 6/1,5 = 4.",
     "2 : rapport des longueurs donné pour le rapport des aires ; 3 : k³, confusion avec les volumes ; 4 : aire de A'B'C' donnée telle quelle ; 5 : rapport lu approximativement.",
     p.render(), "Triangle ABC et son image A'B'C' sur quadrillage")

# M13 — pavé : grande diagonale ------------------------------------------------------------------------------------------------
fig = pave(12, 4, 3, labels=("12 m", "4 m", "3 m"))
item("M13", "Mathématiques", None, "espace", "facile", "calculer", "Distance dans l'espace : diagonale d'un pavé droit (Pythagore deux fois)", "objet technique",
     "Câble tendu dans un entrepôt",
     "Un électricien doit tendre un câble d'un coin au sol A au coin opposé G sous le plafond d'un entrepôt en forme de pavé droit, dont les dimensions figurent "
     "sur la perspective cavalière ci-contre. Il refuse tout détour. Quelle longueur minimale de câble lui faut-il ?",
     ["13 m", "19 m", "12,6 m", "15 m", "169 m"], 1,
     "La grande diagonale AG vérifie AG² = AB² + BC² + CG² = 12² + 4² + 3² = 144 + 16 + 9 = 169, donc AG = √169 = 13 m. "
     "(Pythagore dans le plan de base : AC² = 144 + 16 = 160, puis dans le triangle ACG rectangle en C : AG² = 160 + 9.)",
     "2 : somme des trois dimensions ; 3 : diagonale de la base √160 seule ; 4 : 12 + 3 = 15, calcul limité à une seule face ; 5 : oubli de la racine carrée.",
     fig, "Perspective cavalière de l'entrepôt ABCDEFGH")

# M14 — inéquation ln(x) ≤ 1 lue sur un graphique ---------------------------------------------------------------------------------
p = Plot(0, 5, -2, 2, 440, 300, xstep=1, ystep=1)
p.curve(math.log, 0.05, 5)
p.segment(0, 1, 5, 1, ROUGE, 1.6, dash="6 4")
p.label(4.2, 1.15, "y = 1", ROUGE, 12, "start")
p.dashes_to_axes(math.e, 1)
p.label(math.e, -0.3, "e", ROUGE, 13, "middle", "bold")
item("M14", "Mathématiques", None, "eqlog", "moyen", "raisonner", "Inéquation logarithmique, lecture graphique et ensemble de définition", "document graphique",
     "Seuil d'acidité sur une courbe de laboratoire",
     "Un laborantin utilise la courbe de la fonction ln ci-contre pour repérer les valeurs de x telles que ln x ≤ 1 ; la droite y = 1 est tracée en rouge. "
     "Quel est l'ensemble des solutions de cette inéquation ?",
     ["]0 ; e]", "]−∞ ; e]", "[1 ; e]", "]0 ; 1]", "[e ; +∞["], 1,
     "ln est définie sur ]0 ; +∞[ et strictement croissante ; ln x ≤ 1 = ln e équivaut à 0 < x ≤ e. Sur la figure, la courbe est sous la droite y = 1 pour toutes les abscisses de l'axe jusqu'à e, y compris celles où ln est négatif.",
     "2 : oubli de l'ensemble de définition (x > 0) ; 3 : seules les valeurs où ln x ≥ 0 sont retenues ; 4 : confusion entre ln x ≤ 1 et ln x ≤ 0 ; 5 : sens de l'inégalité inversé.",
     p.render(), "Courbe de ln et droite y = 1")

# M15 — développement en série de sin --------------------------------------------------------------------------------------------
p = Plot(-3.5, 3.5, -2, 2, 460, 300, xstep=1, ystep=1)
p.curve(math.sin, color=NUIT)
p.curve(lambda x: x - x ** 3 / 6, color=ROUGE, dash="6 4")
p.legend([("sin x", NUIT, None), ("P(x)", ROUGE, "6 4")], x=60, y=30)
approx = 0.5 - 0.5 ** 3 / 6
item("M15", "Mathématiques", None, "serie", "difficile", "modéliser", "Développement limité de sin x à l'ordre 3 et approximation numérique", "document technique",
     "Approximation d'un capteur d'angle",
     "La notice d'un capteur d'inclinaison indique qu'il remplace sin x par un polynôme P(x), tracé en pointillés rouges sur la figure ; "
     "les deux courbes sont confondues près de 0 et P(x) est le développement de sin x à l'ordre 3. Quelle valeur approchée P(0,5) le capteur calcule-t-il ?",
     [fmt(round(approx, 4)), "0,5", "0,4583", "0,4875", "0,5208"], 1,
     f"Développement de sin x à l'ordre 3 : P(x) = x − x³/6. P(0,5) = 0,5 − 0,125/6 = 0,5 − 0,020833… ≈ {approx:.4f} (valeur exacte sin 0,5 ≈ 0,4794).".replace(".", ","),
     "2 : ordre 1 seulement (sin x ≈ x) ; 3 : x − x³/3, coefficient 1/3! remplacé par 1/3 ; 4 : x − x²/… formule confondue avec cos ; 5 : signe + au lieu de −.",
     p.render(), "sin x et son polynôme d'approximation P(x) près de 0")

# =====================================================================================================================
# PHYSIQUE (10)
# =====================================================================================================================

# P01 — graphe v(t) : distance = aire ----------------------------------------------------------------------------------------
p = Plot(0, 14, 0, 12, 460, 300, xstep=2, ystep=2, xlabel="t (s)", ylabel="v (m/s)")
p.area(lambda t: 10 * t / 4 if t <= 4 else (10 if t <= 10 else 10 * (12 - t) / 2), 0, 12, OR, 0.22)
p.polyline([(0, 0), (4, 10), (10, 10), (12, 0)], NUIT, 2.4)
d = 0.5 * 4 * 10 + 6 * 10 + 0.5 * 2 * 10
item("P01", "Physique", None, "cine", "moyen", "interpréter", "Diagramme des vitesses : la distance parcourue est l'aire sous v(t)", "donnée brute",
     "Trajet d'une moto-taxi entre deux arrêts",
     "L'enregistreur d'une moto-taxi a tracé la vitesse en fonction du temps entre deux arrêts, du départ à l'arrêt complet (figure). "
     "Le mouvement comporte une phase d'accélération, une phase à vitesse constante et un freinage. Quelle distance la moto a-t-elle parcourue ?",
     [f"{fmt(d)} m", "120 m", "60 m", "100 m", "140 m"], 1,
     f"La distance est l'aire sous la courbe v(t) : triangle (0 à 4 s) = ½ × 4 × 10 = 20 m ; rectangle (4 à 10 s) = 6 × 10 = 60 m ; triangle (10 à 12 s) = ½ × 2 × 10 = 10 m. Total = {fmt(d)} m.",
     "2 : v_max × durée totale (12 × 10) comme si la vitesse était constante ; 3 : seule la phase à vitesse constante ; 4 : triangles comptés comme des rectangles puis erreur ; 5 : aire calculée jusqu'à 14 s.",
     p.render(), "Vitesse de la moto en fonction du temps")

# P02 — chute libre : h(t) → vitesse -------------------------------------------------------------------------------------------
p = Plot(0, 3, 0, 50, 440, 300, xstep=0.5, ystep=10, xlabel="t (s)", ylabel="h (m)", xfmt=lambda v: fmt(v))
p.curve(lambda t: 5 * t * t, 0, 3)
p.dashes_to_axes(2, 20); p.point(2, 20, "(2 ; 20)", dx=8, dy=14); p.dashes_to_axes(1, 5); p.point(1, 5, "(1 ; 5)", dx=8, dy=14)
item("P02", "Physique", None, "cine", "difficile", "modéliser", "Chute libre : h = ½gt², v = gt, lecture de g sur un graphique", "phénomène observé",
     "Chute d'une noix de palme filmée",
     "Une vidéo au ralenti d'une noix de palme tombant d'un palmier a permis de tracer la hauteur de chute h en fonction du temps t (figure) ; on néglige l'air. "
     "La courbe passe par (1 s ; 5 m) et (2 s ; 20 m). Quelle est la vitesse de la noix à l'instant t = 2 s ?",
     ["20 m/s", "10 m/s", "40 m/s", "5 m/s", "15 m/s"], 1,
     "h = ½gt² : avec h(1) = 5 m, g = 10 m/s² (on vérifie h(2) = ½ × 10 × 4 = 20 m). La vitesse est v = gt = 10 × 2 = 20 m/s. "
     "La pente de la courbe en t = 2 s (dérivée de 5t²) vaut bien 10 × 2 = 20 m/s.",
     "2 : vitesse moyenne 20 m / 2 s ; 3 : h/t × 2 ou confusion v = 2gt ; 4 : lecture de h(1) prise pour une vitesse ; 5 : moyenne arithmétique erronée.",
     p.render(), "Hauteur de chute en fonction du temps")

# P03 — plan incliné : composante du poids ------------------------------------------------------------------------------------
fig = plan_incline(30, [("P", -90, 80, ROUGE), ("R", 120, 70, VERT)], masse_label="20 kg")
item("P03", "Physique", None, "poids", "moyen", "calculer", "Décomposition du poids sur un plan incliné : P·sin α et P·cos α", "scène de travail",
     "Fût roulé sur une rampe de camion",
     "Un manutentionnaire retient un fût de 20 kg sur une rampe inclinée de 30° par rapport au sol, sans frottement (figure : poids P et réaction R du plan). "
     "On prend g = 10 N/kg. Quelle force minimale, parallèle à la rampe, doit-il exercer pour empêcher le fût de descendre ?",
     ["100 N", "173 N", "200 N", "20 N", "50 N"], 1,
     "P = mg = 20 × 10 = 200 N. La composante du poids parallèle à la pente vaut P·sin 30° = 200 × 0,5 = 100 N ; c'est elle qu'il faut compenser. "
     "La composante perpendiculaire P·cos 30° ≈ 173 N est équilibrée par la réaction du plan.",
     "2 : composante perpendiculaire (cos) prise pour la composante parallèle ; 3 : poids entier ; 4 : masse confondue avec une force ; 5 : sin 30° appliqué à la masse.",
     fig, "Fût de 20 kg sur une rampe inclinée de 30°")

# P04 — énergie : toboggan ------------------------------------------------------------------------------------------------------
p = Plot(0, 10, 0, 6, 460, 260, xstep=2, ystep=1, xlabel="distance (m)", ylabel="hauteur (m)", grid=False)
p.curve(lambda x: 5 * (1 - x / 8) ** 2 if x <= 8 else 0, 0, 10, color=NUIT, width=3)
p.point(0, 5, "A (départ, v = 0)", dx=10, dy=-8); p.point(8, 0, "B", dx=0, dy=-10, anchor="middle")
p.segment(0, 0, 0, 5, GRIS, 1, dash="4 3"); p.label(0.15, 2.5, "h = 5 m", GRIS, 12, "start")
item("P04", "Physique", None, "energie", "facile", "calculer", "Conservation de l'énergie mécanique : mgh = ½mv²", "événement collectif",
     "Toboggan d'une fête foraine",
     "Le profil d'un toboggan aquatique installé pour une kermesse est donné ci-contre : un enfant part de A sans vitesse, 5 m au-dessus de l'arrivée B. "
     "On néglige les frottements et on prend g = 10 m/s². Quelle est la vitesse de l'enfant en B ?",
     ["10 m/s", "50 m/s", "5 m/s", "7,1 m/s", "100 m/s"], 1,
     "Conservation de l'énergie mécanique entre A et B : mgh = ½mv² ⇒ v = √(2gh) = √(2 × 10 × 5) = √100 = 10 m/s. La masse n'intervient pas.",
     "2 : v = gh sans racine ni facteur 2 ; 3 : v = h confondu ; 4 : √(gh) oubli du facteur 2 ; 5 : v² donné pour v.",
     p.render(), "Profil du toboggan entre A et B")

# P05 — oscillateur : période sur x(t) --------------------------------------------------------------------------------------------
p = Plot(0, 1.0, -4, 4, 460, 280, xstep=0.1, ystep=2, xlabel="t (s)", ylabel="x (cm)", xfmt=lambda v: fmt(round(v, 1)))
p.curve(lambda t: 3 * math.cos(2 * math.pi * t / 0.4))
item("P05", "Physique", None, "oscil", "facile", "interpréter", "Oscillateur harmonique : amplitude, période, fréquence lues sur x(t)", "donnée brute",
     "Vibration d'une machine à coudre",
     "Un capteur fixé sur le bâti d'une machine à coudre industrielle enregistre son déplacement x au cours du temps ; l'oscillogramme est reproduit ci-contre. "
     "Le technicien doit en déduire la fréquence de vibration. Quelle est-elle ?",
     ["2,5 Hz", "0,4 Hz", "3 Hz", "5 Hz", "0,2 Hz"], 1,
     "Sur la courbe, un motif complet se répète toutes les 0,4 s (maximums à t = 0 ; 0,4 ; 0,8 s) : T = 0,4 s. Fréquence f = 1/T = 1/0,4 = 2,5 Hz. L'amplitude, 3 cm, n'intervient pas.",
     "2 : période donnée à la place de la fréquence ; 3 : amplitude confondue avec la fréquence ; 4 : demi-période utilisée (1/0,2) ; 5 : demi-période donnée comme fréquence.",
     p.render(), "Déplacement x du bâti en fonction du temps")

# P06 — onde stationnaire -----------------------------------------------------------------------------------------------------------
fig = corde(3, "L = 1,2 m")
item("P06", "Physique", None, "ondes", "moyen", "raisonner", "Ondes stationnaires sur une corde : L = nλ/2, nœuds et ventres", "scène de travail",
     "Corde de guitare d'un studio",
     "Dans un studio d'enregistrement, une corde de guitare fixée à ses deux extrémités vibre selon le mode représenté ci-contre, avec trois fuseaux sur une longueur L = 1,2 m. "
     "La célérité des ondes sur cette corde est 240 m/s. Quelle est la fréquence de vibration ?",
     ["300 Hz", "100 Hz", "200 Hz", "600 Hz", "150 Hz"], 1,
     "Trois fuseaux : L = 3λ/2 ⇒ λ = 2L/3 = 2 × 1,2/3 = 0,8 m. f = v/λ = 240/0,8 = 300 Hz.",
     "2 : fréquence du fondamental (λ = 2L = 2,4 m) ; 3 : λ = L pris à tort ; 4 : λ = L/3 = 0,4 m (fuseau confondu avec longueur d'onde) ; 5 : λ = 1,6 m, erreur de 2L/n avec n = 1,5.",
     fig, "Mode de vibration de la corde (3 fuseaux) entre les deux points fixes")

# P07 — circuit RLC : impédance ----------------------------------------------------------------------------------------------------
fig = circuit_serie([("R", "R = 30 Ω"), ("L", "XL = 70 Ω"), ("C", "XC = 30 Ω")], ("U = 100 V", "50 Hz"), [("A", "")], ac=True)
item("P07", "Physique", None, "alternatif", "difficile", "calculer", "Circuit RLC série : impédance Z = √(R² + (XL − XC)²), intensité efficace", "document technique",
     "Contrôle d'un circuit de ballast",
     "Le schéma d'un ballast d'éclairage montre un circuit RLC série alimenté en 100 V efficaces à 50 Hz ; les valeurs de R, de la réactance inductive XL et de la réactance capacitive XC sont portées sur la figure. "
     "Quelle intensité efficace l'ampèremètre indique-t-il ?",
     ["2 A", "0,77 A", "3,33 A", "1 A", "1,43 A"], 1,
     "Z = √(R² + (XL − XC)²) = √(30² + (70 − 30)²) = √(900 + 1600) = √2500 = 50 Ω. I = U/Z = 100/50 = 2 A.",
     "2 : réactances additionnées, Z = R + XL + XC = 130 Ω ; 3 : seule la résistance (U/R) ; 4 : condensateur oublié, Z = R + XL = 100 Ω ; 5 : somme algébrique sans le théorème de Pythagore, Z = R + (XL − XC) = 70 Ω.",
     fig, "Circuit RLC série en régime sinusoïdal")

# P08 — transformateur ---------------------------------------------------------------------------------------------------------------
fig = transformateur(1000, 50, "220 V")
item("P08", "Physique", None, "alternatif", "facile", "calculer", "Transformateur parfait : U₂/U₁ = N₂/N₁", "objet technique",
     "Chargeur d'un poste de radio",
     "Le schéma ci-contre, relevé sur la plaque d'un chargeur de radio, représente un transformateur supposé parfait branché sur le secteur de 220 V, "
     "avec les nombres de spires de ses deux enroulements. Quelle tension efficace obtient-on au secondaire ?",
     ["11 V", "4 400 V", "22 V", "44 V", "5,5 V"], 1,
     "Pour un transformateur parfait, U₂/U₁ = N₂/N₁ ⇒ U₂ = 220 × 50/1000 = 11 V. Il s'agit d'un abaisseur de tension (N₂ < N₁).",
     "2 : rapport inversé (N₁/N₂) ; 3 : division par 10 au lieu de 20 ; 4 : erreur d'un facteur 4 ; 5 : division par 40.",
     fig, "Transformateur : primaire 1 000 spires, secondaire 50 spires")

# P09 — cycle P-V : travail = aire ---------------------------------------------------------------------------------------------------
fig = cycle_pv([(0.002, 100000), (0.006, 100000), (0.006, 300000), (0.002, 300000)])
W = (0.006 - 0.002) * (300000 - 100000)
item("P09", "Physique", None, "thermo", "difficile", "interpréter", "Travail échangé au cours d'un cycle : aire du cycle dans le diagramme (P, V)", "document technique",
     "Cycle d'un compresseur d'atelier",
     "Le diagramme (P, V) ci-contre schématise le cycle rectangulaire ABCDA décrit par le gaz d'un petit compresseur de garage, "
     "avec les volumes en m³ et les pressions en Pa lisibles sur les axes. Quelle est la valeur absolue du travail échangé par le gaz au cours d'un cycle ?",
     [f"{fmt(W)} J", "1 200 J", "400 J", "2 400 J", "80 J"], 1,
     f"Sur un cycle, |W| est l'aire du cycle dans le diagramme (P, V) : (0,006 − 0,002) m³ × (300 000 − 100 000) Pa = 0,004 × 200 000 = {fmt(W)} J.",
     "2 : utilisation de P_max × V_max au lieu des écarts ; 3 : ΔV × P_min seulement (pas l'aire du cycle) ; 4 : ΔV × (P_max + P_min)… erreur de lecture ; 5 : erreur d'unité sur le volume (L au lieu de m³).",
     fig, "Cycle ABCDA du gaz dans le diagramme (P, V)")

# P10 — choc mou : quantité de mouvement ----------------------------------------------------------------------------------------------
fig = chariots("4 kg", 6, "2 kg", 0)
vf = 4 * 6 / (4 + 2)
item("P10", "Physique", None, "energie", "moyen", "calculer", "Conservation de la quantité de mouvement dans un choc parfaitement mou", "scène de travail",
     "Accrochage de wagonnets dans une mine",
     "Dans une galerie de mine artisanale, un wagonnet de 4 kg lancé à 6 m/s heurte un wagonnet de 2 kg immobile ; les deux s'accrochent et roulent ensemble (figure). "
     "Les frottements sont négligés. Quelle est la vitesse de l'ensemble juste après le choc ?",
     [f"{fmt(vf)} m/s", "6 m/s", "3 m/s", "12 m/s", "2 m/s"], 1,
     f"Conservation de la quantité de mouvement : m₁v₁ = (m₁ + m₂)v ⇒ v = 4 × 6/(4 + 2) = 24/6 = {fmt(vf)} m/s.",
     "2 : vitesse inchangée (oubli de la masse entraînée) ; 3 : division par 2 sans raison (moyenne des vitesses) ; 4 : m₁v₁/m₂ ; 5 : erreur de calcul 24/12.",
     fig, "Les deux wagonnets avant le choc")

# =====================================================================================================================
# CHIMIE (7)
# =====================================================================================================================

# C01 — courbe de dosage ------------------------------------------------------------------------------------------------------
def ph_curve(v, ca=0.05, va=20.0, cb=0.1):
    na, nb = ca * va, cb * v
    vt = va + v
    if nb < na - 1e-9:
        return -math.log10((na - nb) / vt)
    if nb > na + 1e-9:
        return 14 + math.log10((nb - na) / vt)
    return 7
p = Plot(0, 20, 0, 14, 460, 320, xstep=2, ystep=2, xlabel="V (mL)", ylabel="pH")
p.curve(ph_curve, 0, 20, n=600)
p.dashes_to_axes(10, 7)
item("C01", "Chimie", None, "titrage", "moyen", "interpréter", "Dosage acide fort–base forte : équivalence, C_a·V_a = C_b·V_b", "document technique",
     "Contrôle d'un détartrant à l'acide chlorhydrique",
     "Le contrôle qualité d'une savonnerie dose 20,0 mL d'une solution diluée d'acide chlorhydrique par de la soude à 0,10 mol/L ; la courbe pH = f(V) obtenue, V étant le volume de soude versé, est reproduite ci-contre. "
     "Quelle est la concentration de la solution d'acide dosée ?",
     ["0,050 mol/L", "0,10 mol/L", "0,20 mol/L", "0,025 mol/L", "0,070 mol/L"], 1,
     "Le saut de pH (équivalence, pH = 7 pour un acide fort dosé par une base forte) est à V_E = 10,0 mL. À l'équivalence, C_a·V_a = C_b·V_E ⇒ C_a = 0,10 × 10,0/20,0 = 0,050 mol/L.",
     "2 : concentration de la soude recopiée ; 3 : rapport des volumes inversé ; 4 : division supplémentaire par 2 ; 5 : lecture du pH (7) mélangée à la concentration.",
     p.render(), "Courbe de dosage pH = f(V)")

# C02 — tableau : préparation d'une solution (dilution) ---------------------------------------------------------------------------
fig = table(["Solution", "Concentration", "Volume prélevé", "Volume final"],
            [["Mère S₀", "2,0 mol/L", "—", "—"], ["Fille S₁", "?", "25 mL", "250 mL"]], col_w=[100, 120, 120, 110], first_col_bold=True)
item("C02", "Chimie", None, "solutions", "facile", "calculer", "Dilution : conservation de la quantité de matière C₀V₀ = C₁V₁", "document à lire",
     "Fiche de préparation d'un dispensaire",
     "La fiche de préparation ci-contre, affichée dans la salle de soins d'un dispensaire, indique qu'une solution fille S₁ est obtenue en prélevant 25 mL de la solution mère S₀ "
     "de glucose à 2,0 mol/L et en complétant à 250 mL avec de l'eau distillée. Quelle est la concentration de S₁ ?",
     ["0,20 mol/L", "20 mol/L", "0,50 mol/L", "2,0 mol/L", "0,025 mol/L"], 1,
     "Lors d'une dilution, la quantité de matière se conserve : C₀V₀ = C₁V₁ ⇒ C₁ = C₀V₀/V₁ = 2,0 × 25/250 = 0,20 mol/L (facteur de dilution 10).",
     "2 : rapport des volumes inversé ; 3 : erreur de calcul 2,0 × 25/100 ; 4 : la dilution est ignorée ; 5 : volume prélevé en litres divisé par 1 au lieu du rapport.",
     fig, "Extrait de la fiche de préparation")

# C03 — montage de titrage : identification -----------------------------------------------------------------------------------------
fig = montage_titrage()
item("C03", "Chimie", None, "labo", "facile", "identifier", "Matériel de titrage : burette graduée, erlenmeyer, agitateur magnétique", "document à lire",
     "Inventaire photographié d'un laboratoire",
     "Pour l'inventaire d'un laboratoire d'analyses, un stagiaire annote le schéma ci-contre d'un montage de titrage par des numéros. "
     "Il doit identifier la verrerie qui contient la solution à doser, celle dans laquelle on verse peu à peu la solution titrante. Quel numéro la désigne ?",
     ["1", "2", "3", "4", "5"], 3,
     "La solution à doser est placée dans l'erlenmeyer (3), posé sur l'agitateur magnétique (4) qui entraîne le barreau aimanté (5). La solution titrante est versée depuis la burette graduée (1), dont le robinet (2) règle l'écoulement.",
     "1 : burette graduée, qui contient la solution titrante ; 2 : robinet de la burette ; 4 : agitateur magnétique, qui ne contient rien ; 5 : barreau aimanté.",
     fig, "Montage de titrage numéroté")

# C04 — pile Daniell ----------------------------------------------------------------------------------------------------------------
fig = pile()
item("C04", "Chimie", None, "electrochimie", "moyen", "raisonner", "Pile Daniell : pôles, sens des électrons, force électromotrice E = E°(cathode) − E°(anode)", "document graphique",
     "Pile de démonstration d'une foire scientifique",
     "Sur le stand d'une foire scientifique, la pile schématisée ci-contre associe une lame de zinc dans une solution de Zn²⁺ et une lame de cuivre dans une solution de Cu²⁺, reliées par un pont salin ; "
     "E°(Zn²⁺/Zn) = −0,76 V et E°(Cu²⁺/Cu) = +0,34 V. Quelle affirmation est exacte ?",
     ["Les électrons circulent du zinc vers le cuivre dans le fil et la fem vaut 1,10 V",
      "Les électrons circulent du cuivre vers le zinc dans le fil et la fem vaut 1,10 V",
      "Les électrons traversent le pont salin du zinc vers le cuivre et la fem vaut 0,42 V",
      "Le cuivre est l'anode : il s'oxyde, et la fem vaut 1,10 V",
      "La lame de zinc s'épaissit et la fem vaut 0,42 V"], 1,
     "Le couple de plus faible potentiel (Zn²⁺/Zn) est oxydé : le zinc est l'anode (pôle −), il libère des électrons qui circulent dans le fil vers le cuivre (cathode, pôle +) où Cu²⁺ est réduit. "
     "fem = E°(Cu²⁺/Cu) − E°(Zn²⁺/Zn) = 0,34 − (−0,76) = 1,10 V.",
     "2 : sens des électrons inversé ; 3 : les électrons ne traversent jamais le pont salin (ce sont des ions), et 0,42 = 0,76 − 0,34 est une soustraction en valeurs absolues ; 4 : anode et cathode inversées ; 5 : la lame de zinc se consomme.",
     fig, "Schéma de la pile zinc–cuivre")

# C05 — cases quantiques -----------------------------------------------------------------------------------------------------------------
fig = cases_quantiques([("1s", [2]), ("2s", [2]), ("2p", [2, 2, 2]), ("3s", [2]), ("3p", [2, 1, 1])])
item("C05", "Chimie", None, "atome", "moyen", "identifier", "Configuration électronique, règle de Hund, numéro atomique", "document graphique",
     "Fiche d'un élément dans un manuel de chimie",
     "Une fiche de manuel de chimie, reproduite ci-contre, présente le diagramme de cases quantiques de l'état fondamental d'un atome neutre. "
     "En comptant les électrons représentés et en appliquant la règle de Hund, quel est le numéro atomique Z de cet élément ?",
     ["16", "14", "18", "6", "8"], 1,
     "Électrons : 1s² 2s² 2p⁶ 3s² 3p⁴ = 2 + 2 + 6 + 2 + 4 = 16. Atome neutre : Z = 16, c'est le soufre. Dans 3p, la règle de Hund impose une case doublement occupée et deux cases simplement occupées.",
     "2 : oubli des deux électrons célibataires de 3p ; 3 : 3p compté comme saturé ; 4 : seule la couche de valence 3s² 3p⁴ est comptée ; 5 : nombre de cases comptées au lieu des électrons.",
     fig, "Diagramme de cases quantiques de l'atome")

# C06 — décroissance radioactive -----------------------------------------------------------------------------------------------------------
p = Plot(0, 32, 0, 100, 460, 300, xstep=4, ystep=20, xlabel="t (jours)", ylabel="activité (%)")
p.curve(lambda t: 100 * 0.5 ** (t / 8))
p.dashes_to_axes(8, 50); p.dashes_to_axes(16, 25); p.dashes_to_axes(24, 12.5)
item("C06", "Chimie", None, "noyau", "difficile", "interpréter", "Décroissance radioactive : période (demi-vie), fraction restante après n périodes", "document technique",
     "Gestion d'un déchet radioactif à l'hôpital",
     "Le service de médecine nucléaire d'un hôpital suit l'activité d'un flacon d'iode 131 ; la courbe ci-contre donne l'activité en pourcentage de la valeur initiale au cours des jours. "
     "Le flacon peut être jeté quand l'activité est tombée en dessous de 10 %. Au bout de combien de jours, au minimum parmi ces valeurs, cette condition est-elle remplie ?",
     ["32 jours", "24 jours", "16 jours", "8 jours", "80 jours"], 1,
     "Lecture : l'activité tombe à 50 % en 8 jours, c'est la période T. Après n périodes il reste (1/2)ⁿ : 24 j → 12,5 % (encore > 10 %) ; 32 j → 6,25 % (< 10 %). La réponse est 32 jours.",
     "2 : 12,5 % confondu avec « moins de 10 % » ; 3 : deux périodes (25 %) ; 4 : une période ; 5 : raisonnement linéaire 10 % × 8 j.",
     p.render(), "Activité relative de l'iode 131 en fonction du temps")

# C07 — chromatographie : rapport frontal -------------------------------------------------------------------------------------------------
fig = chromatogramme([("E", [3.0]), ("R", [6.0]), ("M", [3.0, 6.0])], 8.0)
item("C07", "Chimie", None, "separation", "moyen", "calculer", "Chromatographie sur couche mince : rapport frontal R_f = h/H, identification d'un mélange", "document à lire",
     "Analyse d'un colorant alimentaire au marché",
     "Un inspecteur analyse un colorant M vendu au marché par chromatographie, à côté de deux colorants de référence E et R ; le chromatogramme obtenu est reproduit ci-contre, avec sa règle en centimètres. "
     "Quel est le rapport frontal du constituant commun à E et M ?",
     ["0,375", "0,75", "3", "0,5", "2,67"], 1,
     "Hauteur du front du solvant H = 8,0 cm ; la tache commune à E et M est à h = 3,0 cm. R_f = h/H = 3,0/8,0 = 0,375. Le colorant M est un mélange de E et de R.",
     "2 : R_f de la tache R (6/8) ; 3 : hauteur de la tache donnée sans division ; 4 : tache de E rapportée à celle de R (3/6) ; 5 : rapport inversé H/h.",
     fig, "Chromatogramme des dépôts E, R et M")

# =====================================================================================================================
# SVT (8)
# =====================================================================================================================

# S01 — cycle menstruel : hormones -----------------------------------------------------------------------------------------------------------
p = Plot(0, 28, 0, 10, 480, 300, xstep=2, ystep=2, xlabel="jour du cycle", ylabel="taux (u.a.)", grid=False)
p.curve(lambda d: 8 * math.exp(-((d - 14) ** 2) / 2.2) + 0.5, color=ROUGE)
p.curve(lambda d: 4 * math.exp(-((d - 12.5) ** 2) / 8) + 0.4 + 1.5 * math.exp(-((d - 22) ** 2) / 20), color=NUIT, dash="6 4")
p.curve(lambda d: 6 * math.exp(-((d - 21) ** 2) / 12) + 0.2, color=VERT)
p.legend([("LH", ROUGE, None), ("œstrogènes", NUIT, "6 4"), ("progestérone", VERT, None)], x=300, y=30)
item("S01", "SVT", "Biologie", "repro", "facile", "interpréter", "Cycle menstruel : pic de LH et ovulation, rôle de la progestérone", "document à lire",
     "Courbes hormonales d'un carnet de suivi",
     "Le carnet de suivi remis par une sage-femme comporte le graphique ci-contre : taux de trois hormones au cours d'un cycle de 28 jours, sans règles anormales. "
     "Une patiente demande à quel jour l'ovulation a eu lieu. En s'appuyant sur la courbe adéquate, que doit répondre la sage-femme ?",
     ["Vers le 14ᵉ jour, juste après le pic de LH", "Vers le 21ᵉ jour, au maximum de progestérone", "Vers le 1ᵉʳ jour, au début du cycle",
      "Vers le 28ᵉ jour, à la fin du cycle", "Vers le 7ᵉ jour, quand les œstrogènes commencent à monter"], 1,
     "L'ovulation est déclenchée par le pic de LH, visible au 14ᵉ jour sur la courbe rouge ; elle survient dans les 24 à 36 heures qui suivent. "
     "La montée de progestérone (courbe verte) après le 14ᵉ jour est la conséquence de l'ovulation (corps jaune), pas sa cause.",
     "2 : confusion entre le pic de progestérone (phase lutéale) et l'ovulation ; 3 et 4 : début et fin du cycle correspondent aux règles ; 5 : la montée des œstrogènes précède l'ovulation d'une semaine.",
     p.render(), "Taux hormonaux au cours d'un cycle de 28 jours")

# S02 — échiquier dihybride ------------------------------------------------------------------------------------------------------------------
g = ["AB", "Ab", "aB", "ab"]
def cel(m, f):
    k = lambda c: (c.lower(), c.islower())
    return "".join(sorted(m[0] + f[0], key=k)) + "".join(sorted(m[1] + f[1], key=k))
fig = punnett(g, g, cel, w_cell=66)
item("S02", "SVT", "Biologie", "genet", "moyen", "calculer", "Dihybridisme : échiquier de croisement F2, proportions 9:3:3:1", "scène de travail",
     "Sélection de maïs dans une coopérative",
     "Une coopérative agricole croise des plants de maïs doubles hétérozygotes AaBb (A : grain coloré, a : incolore ; B : grain lisse, b : ridé), gènes indépendants. "
     "L'échiquier ci-contre donne les génotypes de la F2. Quelle proportion de plants à grains incolores et ridés attend-on ?",
     ["1/16", "3/16", "9/16", "1/4", "4/16"], 1,
     "Le phénotype incolore et ridé exige le génotype double récessif aabb, qui n'apparaît que dans une case sur les 16 de l'échiquier (gamètes ab × ab) : 1/16. Les autres classes sont 9/16 colorés lisses, 3/16 colorés ridés, 3/16 incolores lisses.",
     "2 : proportion d'une classe simple récessive ; 3 : classe double dominante ; 4 : raisonnement monohybride (1/4 de aa) ; 5 : nombre de cases contenant aa ou bb mal compté.",
     fig, "Échiquier de croisement AaBb × AaBb")

# S03 — arbre généalogique : daltonisme ---------------------------------------------------------------------------------------------------------
fig = pedigree(
    [[{"id": "I1", "sexe": "M", "atteint": False, "label": "1"}, {"id": "I2", "sexe": "F", "atteint": False, "label": "2"}],
     [{"id": "II1", "sexe": "M", "atteint": True, "label": "1"}, {"id": "II2", "sexe": "F", "atteint": False, "label": "2"}, {"id": "II3", "sexe": "M", "atteint": False, "label": "3"}],
     [{"id": "III1", "sexe": "M", "atteint": False, "label": "1", "q": True}]],
    [("I1", "I2"), ("II2", "II3")], [(0, ["II1", "II2"]), (1, ["III1"])])
item("S03", "SVT", "Biologie", "genhum", "difficile", "raisonner", "Hérédité récessive liée à l'X : femmes conductrices, probabilités", "document à lire",
     "Arbre généalogique dressé par un ophtalmologue",
     "Un ophtalmologue a dressé l'arbre ci-contre pour le daltonisme, anomalie récessive liée au chromosome X. Le garçon II1 est atteint ; ses parents I1 et I2 sont sains, "
     "ainsi que sa sœur II2 et le mari de celle-ci, II3. Quelle est la probabilité que leur fils III1 soit daltonien ?",
     ["1/4", "1/2", "0", "1", "1/8"], 1,
     "I1 (sain) est X^D Y ; II1 étant X^d Y, sa mère I2 est conductrice X^D X^d. II2 a reçu X^D de son père et X^D ou X^d de sa mère : P(II2 conductrice) = 1/2. "
     "Si elle l'est, un fils reçoit X^d avec la probabilité 1/2. Donc P(III1 atteint) = 1/2 × 1/2 = 1/4.",
     "2 : II2 supposée conductrice à coup sûr ; 3 : on croit qu'une mère saine ne transmet pas ; 4 : confusion avec un fils d'une mère atteinte ; 5 : multiplication par un 1/2 de trop (le sexe de III1 est déjà connu).",
     fig, "Arbre généalogique : daltonisme (individus atteints en noir)")

# S04 — réponse immunitaire primaire / secondaire --------------------------------------------------------------------------------------------------
p = Plot(0, 60, 0, 10, 480, 300, xstep=10, ystep=2, xlabel="jours", ylabel="anticorps (u.a.)", grid=False)
p.curve(lambda t: (2.2 * math.exp(-((t - 14) ** 2) / 40) if t < 30 else 0) + (9 * math.exp(-((t - 38) ** 2) / 40) * (1 - math.exp(-(t - 30) / 1.5)) if t >= 30 else 0) + 0.1, n=600)
p.segment(0, 0, 0, 9.5, ROUGE, 1.4, dash="4 3"); p.label(1, 9.2, "1ʳᵉ injection", ROUGE, 12, "start")
p.segment(30, 0, 30, 9.5, ROUGE, 1.4, dash="4 3"); p.label(31, 9.2, "2ᵉ injection", ROUGE, 12, "start")
item("S04", "SVT", "Biologie", "immuno", "moyen", "interpréter", "Mémoire immunitaire : réponse secondaire plus rapide et plus intense, principe de la vaccination", "document à lire",
     "Carnet de vaccination d'un éleveur",
     "La notice d'un vaccin vétérinaire, consultée par un éleveur de volailles, montre le taux d'anticorps d'un animal après une première injection au jour 0 et une seconde au jour 30 (figure). "
     "Quelle conclusion correcte peut-il tirer de la comparaison des deux réponses ?",
     ["La seconde réponse est plus rapide et plus intense grâce aux lymphocytes mémoire", "La seconde injection est inutile puisque les anticorps étaient déjà présents",
      "La première réponse est plus intense parce que l'antigène est nouveau", "Les anticorps de la première injection persistent sans baisser jusqu'au jour 60",
      "La seconde réponse est due aux globules rouges activés"], 1,
     "Après la seconde injection, le taux d'anticorps monte plus vite (quelques jours) et environ quatre fois plus haut : c'est la réponse secondaire, due aux lymphocytes B et T mémoire formés lors du premier contact. "
     "C'est le fondement des rappels de vaccination.",
     "2 : la courbe montre au contraire que le premier taux retombe vers 0 avant le jour 30 ; 3 : inversion des intensités lues ; 4 : contredit par la baisse visible entre 20 et 30 jours ; 5 : les globules rouges ne participent pas à l'immunité.",
     p.render(), "Taux d'anticorps après deux injections du même antigène")

# S05 — quantité d'ADN au cours du cycle cellulaire ---------------------------------------------------------------------------------------------
p = Plot(0, 24, 0, 5, 480, 280, xstep=4, ystep=1, xlabel="temps (h)", ylabel="ADN par cellule (u.a.)", grid=False)
p.polyline([(0, 2), (8, 2), (16, 4), (20, 4), (22, 4), (22, 2), (24, 2)], NUIT, 2.4)
for a, b, lab in ((0, 8, "G1"), (8, 16, "S"), (16, 22, "G2 + M"), (22, 24, "G1")):
    p.segment(b, 0, b, 5, GRIS, 1, dash="4 3"); p.label((a + b) / 2, 0.45, lab, ROUGE, 13, "middle", "bold")
item("S05", "SVT", "Biologie", "cyto", "moyen", "interpréter", "Cycle cellulaire : réplication de l'ADN en phase S, division en M", "document à lire",
     "Mesures d'un laboratoire de cytologie",
     "Un laboratoire de cytologie a mesuré la quantité d'ADN par cellule au cours d'un cycle cellulaire de 24 heures ; le graphique ci-contre délimite les phases. "
     "Entre la 8ᵉ et la 16ᵉ heure, la quantité d'ADN double. Que se passe-t-il dans la cellule pendant cet intervalle ?",
     ["La réplication de l'ADN (phase S)", "La séparation des chromatides (anaphase)", "La condensation des chromosomes (prophase)",
      "La cytodiérèse, partage du cytoplasme", "La croissance de la cellule sans synthèse d'ADN (G1)"], 1,
     "Le doublement progressif de la quantité d'ADN correspond à la réplication semi-conservative, en phase S de l'interphase ; chaque chromosome passe à deux chromatides. "
     "La chute brutale à 22 h correspond à la mitose, qui répartit l'ADN entre deux cellules filles.",
     "2 et 4 : événements de la mitose, visibles par la chute brutale à 22 h ; 3 : la prophase ne change pas la quantité d'ADN ; 5 : G1 est le plateau initial à 2 u.a.",
     p.render(), "Quantité d'ADN par cellule au cours du cycle")

# S06 — réseau trophique ------------------------------------------------------------------------------------------------------------------------
fig = reseau_trophique([("h", "herbes aquatiques", 90, 250), ("i", "insectes", 90, 140), ("t", "tilapias", 260, 190), ("hr", "héron", 430, 110), ("c", "crocodile", 430, 250)],
                       [("h", "i"), ("h", "t"), ("i", "t"), ("t", "hr"), ("t", "c"), ("hr", "c")])
item("S06", "SVT", "Écologie", "ecosys", "facile", "identifier", "Réseau trophique : producteurs, consommateurs, niveaux trophiques", "phénomène observé",
     "Réseau alimentaire d'un étang piscicole",
     "Le gestionnaire d'un étang piscicole a schématisé ci-contre les relations alimentaires observées ; chaque flèche va de l'organisme mangé vers celui qui le mange. "
     "Il veut situer le héron dans ce réseau. Quel(s) niveau(x) trophique(s) le héron occupe-t-il ?",
     ["Consommateur secondaire ou tertiaire, selon la chaîne considérée", "Consommateur primaire uniquement", "Producteur",
      "Consommateur secondaire uniquement", "Consommateur quaternaire uniquement"], 1,
     "Le héron ne mange que des tilapias. Dans la chaîne herbes → tilapia → héron, le tilapia est consommateur primaire et le héron secondaire ; dans la chaîne herbes → insectes → tilapia → héron, "
     "le tilapia est secondaire et le héron tertiaire. Un même organisme peut donc occuper plusieurs niveaux dans un réseau.",
     "2 : le héron ne mange pas de végétaux ; 3 : seules les herbes aquatiques sont productrices ; 4 : oubli de la chaîne passant par les insectes ; 5 : le niveau quaternaire est atteint par le crocodile via le héron.",
     fig, "Réseau trophique de l'étang")

# S07 — frise géologique ---------------------------------------------------------------------------------------------------------------------------
fig = frise([("Formation de la Terre", 4600, "− 4 600 Ma"), ("Premières cellules", 3800, "− 3 800 Ma"), ("Explosion cambrienne", 541, "− 541 Ma"),
             ("Extinction des dinosaures", 66, "− 66 Ma")], 4600, 0, titre="Quelques repères de l'histoire de la Terre (Ma = millions d'années avant le présent)")
item("S07", "SVT", "Géologie & Évolution", "geol", "facile", "calculer", "Échelle des temps géologiques : ordres de grandeur, durée du Phanérozoïque", "document à lire",
     "Frise du musée géologique",
     "La frise ci-contre, affichée dans un musée géologique, situe quelques repères de l'histoire de la Terre en millions d'années (Ma) avant le présent. "
     "Un visiteur veut savoir quelle fraction de l'âge de la Terre s'est écoulée depuis l'explosion cambrienne. Quelle réponse est la plus proche ?",
     ["Environ 12 %", "Environ 50 %", "Environ 1 %", "Environ 25 %", "Environ 85 %"], 1,
     "Âge de la Terre : 4 600 Ma ; explosion cambrienne : 541 Ma. Fraction = 541/4 600 ≈ 0,118, soit environ 12 %. Le Phanérozoïque, riche en fossiles, ne représente donc qu'un peu plus d'un dixième de l'histoire terrestre.",
     "2 : impression visuelle fausse due à la place occupée par le texte ; 3 : confusion avec 66 Ma (66/4 600 ≈ 1,4 %) ; 4 : estimation grossière ; 5 : fraction écoulée avant le Cambrien.",
     fig, "Repères chronologiques (Ma = millions d'années avant le présent)")

# S08 — croissance logistique -------------------------------------------------------------------------------------------------------------------------
K = 800
p = Plot(0, 20, 0, 1000, 480, 300, xstep=2, ystep=200, xlabel="semaines", ylabel="nombre de tilapias")
p.curve(lambda t: K / (1 + 15 * math.exp(-0.5 * t)))
p.segment(0, K, 20, K, ROUGE, 1.4, dash="6 4")
item("S08", "SVT", "Écologie", "ecoconcepts", "moyen", "interpréter", "Dynamique d'une population : croissance logistique, capacité limite du milieu", "donnée brute",
     "Suivi d'un bassin d'alevinage",
     "Le registre d'un bassin d'alevinage donne l'effectif de tilapias au fil des semaines après l'ensemencement de 50 alevins, sans pêche ni apport ; la courbe est reproduite ci-contre, avec une droite en pointillés rouges. "
     "Que représente la valeur 800 indiquée par cette droite ?",
     ["La capacité limite du milieu, effectif maximal que les ressources du bassin peuvent entretenir", "Le nombre d'alevins introduits au départ",
      "L'effectif atteint au bout de deux semaines", "Le taux de croissance de la population par semaine", "La quantité de nourriture distribuée chaque semaine"], 1,
     "La courbe en S (logistique) croît d'abord vite puis se stabilise sous une asymptote : l'effectif ne dépasse pas 800 individus, limite imposée par l'espace, l'oxygène et la nourriture disponibles : c'est la capacité limite (ou capacité de charge) K du milieu.",
     "2 : l'effectif initial se lit à t = 0 (50) ; 3 : à deux semaines l'effectif est voisin de 120 ; 4 : un taux de croissance n'est pas un effectif ; 5 : aucune information sur la nourriture n'est portée sur le graphique.",
     p.render(), "Effectif de la population de tilapias au cours du temps")

# =====================================================================================================================
# Position de la bonne réponse : permutation déterministe par item, avec renumérotation des erreurs des distracteurs
import random
import re


def melanger(it: dict) -> None:
    rnd = random.Random(it["id"])
    perm = list(range(5))
    while perm[it["reponse"] - 1] == 0 and rnd.random() < 0.8:  # évite que la clé reste trop souvent en 1
        rnd.shuffle(perm)
    rnd.shuffle(perm)
    # perm[j] = ancien indice placé en position j
    props = [it["propositions"][perm[j]] for j in range(5)]
    nouveau_num = {perm[j] + 1: j + 1 for j in range(5)}
    it["propositions"] = props
    it["reponse"] = nouveau_num[it["reponse"]]
    parts = []
    for part in re.split(r"\s;\s", it["erreurs_distracteurs"]):
        m = re.match(r"^\s*([\d,\s]+(?:et\s*\d)?)\s*:\s*(.*)$", part)
        if not m:
            parts.append((99, part.strip()))
            continue
        nums = [int(x) for x in re.findall(r"\d", m.group(1))]
        nn = sorted(nouveau_num[n] for n in nums)
        lab = " et ".join(str(n) for n in nn) if len(nn) <= 2 else ", ".join(str(n) for n in nn)
        parts.append((nn[0], f"{lab} : {m.group(2).strip().rstrip('.')}"))
    it["erreurs_distracteurs"] = " ; ".join(t for _, t in sorted(parts, key=lambda x: x[0])) + "."


for it in ITEMS:
    if it["id"] != "FIG1-C03":  # les propositions sont les numéros de la figure : ordre naturel conservé
        melanger(it)
print("positions de la clé :", Counter(i["reponse"] for i in ITEMS) if False else None)
assert len(ITEMS) == 40, len(ITEMS)
from collections import Counter
print(Counter(i["discipline"] for i in ITEMS), Counter(i["difficulte"] for i in ITEMS), "clé :", dict(Counter(i["reponse"] for i in ITEMS)))
out = Path(__file__).parent / "lot1_sciences.json"
out.write_text(json.dumps({"source": "lot 1 — figures Sciences (préparé hors plateforme)", "items": ITEMS}, ensure_ascii=False, indent=1), encoding="utf-8")
print("écrit", out, f"{out.stat().st_size / 1024:.0f} ko")

# planche de contrôle visuel
html = ["<!doctype html><meta charset='utf-8'><style>body{font-family:system-ui;margin:20px;max-width:1100px}.it{border:1px solid #ddd;border-radius:10px;padding:14px;margin:14px 0;page-break-inside:avoid}"
        "svg{max-width:100%;height:auto}.t{font-weight:600;color:#1B2A4A}.p{margin:4px 0}.ok{color:#2E7D5B;font-weight:700}small{color:#777}</style>"]
for it in ITEMS:
    html.append(f"<div class='it'><div class='t'>{it['id']} · {it['discipline']} · {it['difficulte']} · <small>{it['chapitre']}</small></div><h3>{it['titre']}</h3><p>{it['tige']}</p>"
                f"<div style='display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap'><div style='flex:1;min-width:380px'>{it['figure_svg']}<br><small><i>{it['figure_legende']}</i></small></div><div style='flex:1;min-width:300px'>"
                + "".join(f"<div class='p {'ok' if k == it['reponse'] else ''}'>{k}. {p}</div>" for k, p in enumerate(it['propositions'], 1))
                + f"<p><b>Correction.</b> {it['correction_detaillee']}</p><small>{it['erreurs_distracteurs']}</small></div></div></div>")
(Path(__file__).parent / "planche_lot1.html").write_text("".join(html), encoding="utf-8")
