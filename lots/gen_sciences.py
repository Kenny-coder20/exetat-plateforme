"""Générateurs de questions à figures — Mathématiques, Physique, Chimie, SVT (épreuves M.46 et M.07).

Chaque gabarit : des paramètres tirés au sort, une figure tracée par code, trois à quatre questions dont la clé est
calculée. Contextes tournants (métiers, lieux, documents), sans cadre scolaire.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from figures import GRIS, NUIT, OR, ROUGE, VERT, Plot, cases_quantiques, chromatogramme, circuit_serie, lentille, pedigree, pile, plan_incline, punnett, reseau_trophique, table, transformateur, tree  # noqa: E402
from outils import chapitre, distracteurs, fmt, item  # noqa: E402

ITEMS: list[dict] = []
LIEUX = ["Kikwit", "Mbandaka", "Kindu", "Uvira", "Boma", "Bunia", "Isiro", "Gemena", "Kalemie", "Tshikapa", "Likasi", "Butembo", "Inongo", "Lisala", "Kenge", "Idiofa", "Kamina", "Kabinda", "Lodja", "Mwene-Ditu", "Zongo", "Moanda", "Goma", "Matadi", "Kananga", "Kisangani", "Bukavu", "Kolwezi"]


def lieu(rnd):
    return rnd.choice(LIEUX)


SAUTES: list[str] = []


def ajouter(**kw):
    """Ajoute l'item ; une variante dont les distracteurs entrent en collision est simplement sautée (tracée)."""
    try:
        ITEMS.append(item(**kw))
    except AssertionError as e:
        SAUTES.append(str(e)[:120])


# ======================================================================================================================
# MATHÉMATIQUES
# ======================================================================================================================

def m_exp(rnd: random.Random, k: int):
    """Courbe f(x) = a·e^(bx) + c : lecture, résolution f(x)=k, seuil (décision)."""
    a = rnd.choice([1, 2, 3]); b = rnd.choice([0.5, 1, -0.5, -1]); c = rnd.choice([-3, -2, -1, 1, 2])
    f = lambda x: a * math.exp(b * x) + c
    xs = (-3, 3) if b > 0 else (-3, 4)
    ymax = max(f(xs[0]), f(xs[1]), c + 1); ymin = min(f(xs[0]), f(xs[1]), c - 1)
    p = Plot(xs[0], xs[1], math.floor(ymin) - 1, min(math.ceil(ymax) + 1, 14), xstep=1, ystep=1 if ymax < 8 else 2)
    p.curve(f)
    p.segment(xs[0], c, xs[1], c, ROUGE, 1.2, dash="6 4"); p.label(xs[0] + 0.2, c + 0.3, f"y = {fmt(c)}", ROUGE, 12, "start")
    p.point(0, f(0), f"A(0 ; {fmt(f(0))})", dx=8, dy=-8)
    fig, leg = p.render(), f"Courbe de f(x) = {fmt(a)}·e^({fmt(b)}x) {'+' if c > 0 else '−'} {abs(c)} et son asymptote"
    ctx = rnd.choice([("Un ingénieur de la SNEL modélise la charge d'un transformateur par", "charge"), ("Un pisciculteur suit la croissance de la biomasse de son étang par", "biomasse"),
                      ("Une pharmacienne modélise la concentration d'un médicament dans le sang par", "concentration"), ("Un météorologue représente l'écart de pression par", "écart de pression")])
    chap = chapitre("Mathématiques", "exponentielles", "logarithmiques")
    kk = rnd.choice([v for v in (c + 1, c + 2, c + 4, c + 6) if (v - c) / a > 0])
    xk = math.log((kk - c) / a) / b
    # Q1 : asymptote
    ajouter(id_=f"FIG2-MA-exp-{k}-1", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="facile", type_item="classique", competence="interpréter",
            savoir="Limite et asymptote horizontale d'une fonction exponentielle", famille="document technique", titre="Asymptote d'une courbe exponentielle",
            tige=f"{ctx[0]} la fonction f(x) = {fmt(a)}·e^({fmt(b)}x) {'+' if c > 0 else '−'} {abs(c)}, dont la courbe est tracée ci-contre avec une droite en pointillés rouges. "
                 f"Il veut nommer cette droite sur son rapport. Quelle est l'équation de l'asymptote horizontale de la courbe ?",
            bonne=f"y = {fmt(c)}", faux=[f"x = {fmt(c)}", f"y = {fmt(a)}", f"y = {fmt(f(0))}", f"y = {fmt(c + a)}"],
            correction=f"Quand x tend vers {'−∞' if b > 0 else '+∞'}, e^({fmt(b)}x) tend vers 0, donc f(x) tend vers {fmt(c)} : la droite y = {fmt(c)} est asymptote horizontale (pointillés rouges).",
            erreurs=["asymptote verticale confondue", "coefficient a pris pour la limite", "ordonnée du point A", "valeur f(0) + … erreur de limite"], figure=fig, legende=leg, rnd=rnd)
    # Q2 : résolution f(x) = kk
    ajouter(id_=f"FIG2-MA-exp-{k}-2", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chapitre("Mathématiques", "équations", "log-exp"), difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Résolution d'une équation exponentielle par le logarithme", famille="document technique", titre=f"Résolution d'une équation sur la courbe",
            tige=f"Sur la courbe ci-contre de f(x) = {fmt(a)}·e^({fmt(b)}x) {'+' if c > 0 else '−'} {abs(c)}, on cherche l'abscisse exacte du point d'ordonnée {fmt(kk)}, "
                 f"c'est-à-dire la solution de f(x) = {fmt(kk)}. Quelle est cette solution ?",
            bonne=f"x = ln({fmt((kk - c) / a)})/{fmt(b)}" if b != 1 else f"x = ln({fmt((kk - c) / a)})",
            faux=[f"x = ln({fmt(kk / a)})/{fmt(b)}" if b != 1 else f"x = ln({fmt(kk / a)})", f"x = e^({fmt((kk - c) / a)})", f"x = {fmt((kk - c) / a)}", f"x = ln({fmt(kk - c)})/{fmt(b)}" if a != 1 else f"x = ln({fmt(kk - c)})·{fmt(b)}"],
            correction=f"f(x) = {fmt(kk)} ⇔ {fmt(a)}·e^({fmt(b)}x) = {fmt(kk - c)} ⇔ e^({fmt(b)}x) = {fmt((kk - c) / a)} ⇔ {fmt(b)}x = ln({fmt((kk - c) / a)}) ⇔ x = ln({fmt((kk - c) / a)})/{fmt(b)} ≈ {fmt(xk, 2)}, cohérent avec la lecture graphique.",
            erreurs=["oubli de soustraire c avant de diviser", "confusion ln / exp", "oubli du logarithme", "oubli de diviser par a"], figure=fig, legende=leg, rnd=rnd)
    # Q3 : décision seuil
    seuil = kk
    ajouter(id_=f"FIG2-MA-exp-{k}-3", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Interprétation d'une courbe exponentielle : franchissement d'un seuil", famille="décision professionnelle", titre="Seuil atteint ou non",
            tige=f"{ctx[0]} f(x) = {fmt(a)}·e^({fmt(b)}x) {'+' if c > 0 else '−'} {abs(c)} (courbe ci-contre, x en heures). Une alarme doit se déclencher dès que la grandeur {'dépasse' if b > 0 else 'passe sous'} {fmt(seuil)}. "
                 f"Doit-il programmer l'alarme pour un instant précis, et lequel ?",
            bonne=f"Oui, à x ≈ {fmt(xk, 2)} h, car f(x) = {fmt(seuil)} a pour solution ln({fmt((kk - c) / a)})/{fmt(b)}",
            faux=[f"Non, car la courbe tend vers {fmt(c)} et n'atteint jamais {fmt(seuil)}", f"Oui, à x = {fmt(seuil)} h, car le seuil se lit sur l'axe des abscisses",
                  f"Oui, à x ≈ {fmt(math.log(abs(kk) / a) / b if kk != 0 else 0, 2)} h, car e^({fmt(b)}x) = {fmt(kk / a)}", f"Non, car f(0) = {fmt(f(0))} est déjà {'au-dessus' if f(0) > seuil else 'en dessous'} du seuil"],
            correction=f"Le seuil {fmt(seuil)} est atteint quand {fmt(a)}·e^({fmt(b)}x) = {fmt(kk - c)}, soit x = ln({fmt((kk - c) / a)})/{fmt(b)} ≈ {fmt(xk, 2)} h ; la courbe le confirme. L'asymptote y = {fmt(c)} n'empêche pas d'atteindre {fmt(seuil)}, qui est du bon côté.",
            erreurs=["asymptote confondue avec une borne jamais franchie", "seuil lu sur le mauvais axe", "oubli du terme constant c", "valeur initiale confondue avec le franchissement"], figure=fig, legende=leg, rnd=rnd)


def m_batons(rnd: random.Random, k: int):
    """Diagramme en bâtons : moyenne, médiane, décision (seuil de rendement)."""
    vals = list(range(rnd.choice([0, 1, 2]), rnd.choice([0, 1, 2]) + rnd.choice([5, 6])))
    eff = [rnd.randint(1, 8) for _ in vals]
    N = sum(eff); moy = sum(v * e for v, e in zip(vals, eff)) / N
    cum, med = 0, None
    for v, e in zip(vals, eff):
        cum += e
        if cum >= N / 2 and med is None:
            med = v
    mode = vals[eff.index(max(eff))]
    ctx = rnd.choice([("d'un garage", "pannes par camion sur l'année", "camions"), ("d'un centre de santé", "consultations par jour sur un mois", "jours"), ("d'une coopérative", "sacs vendus par membre en une semaine", "membres"),
                      ("d'un port fluvial", "pirogues accostées par jour", "jours"), ("d'une boulangerie", "fournées par jour", "jours")])
    dec = 1 - vals[0]
    p = Plot(vals[0] + dec - 0.7, vals[-1] + dec + 0.7, 0, max(eff) + 2, 420, 280, xstep=1, ystep=1, xlabel=ctx[1].split(" par")[0], ylabel="effectif", grid=False, xfmt=lambda v, d=dec: fmt(v - d))
    p.bars([(v + dec, e) for v, e in zip(vals, eff)], 0.55)
    fig, leg = p.render(), f"Distribution observée ({ctx[1]})"
    chap = chapitre("Mathématiques", "statistiques", "dispersion")
    ajouter(id_=f"FIG2-MA-bat-{k}-1", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Moyenne d'une série statistique lue sur un diagramme en bâtons", famille="donnée brute", titre="Moyenne d'une distribution",
            tige=f"Le registre {ctx[0]} de {lieu(rnd)} donne, sur {N} {ctx[2]}, le nombre de {ctx[1]} ; le diagramme en bâtons ci-contre en montre la distribution "
                 f"(hauteur = effectif). Quelle est la moyenne de cette série, arrondie au centième ?",
            bonne=fmt(moy, 2), faux=[fmt(sum(vals) / len(vals), 2) if fmt(sum(vals) / len(vals), 2) != fmt(moy, 2) else fmt(moy + 0.5, 2), fmt(mode), fmt(N / len(vals), 2), fmt(sum(v * e for v, e in zip(vals, eff)) / len(vals), 2)],
            correction=f"N = {' + '.join(map(str, eff))} = {N}. Σxᵢnᵢ = {' + '.join(f'{v}·{e}' for v, e in zip(vals, eff))} = {sum(v * e for v, e in zip(vals, eff))}. Moyenne = {sum(v * e for v, e in zip(vals, eff))}/{N} ≈ {fmt(moy, 2)}.",
            erreurs=["moyenne des valeurs sans pondération", "mode pris pour la moyenne", "effectif moyen par valeur", "division par le nombre de valeurs au lieu de N"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-MA-bat-{k}-2", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="moyen", type_item="classique", competence="interpréter",
            savoir="Médiane et mode d'une série statistique discrète", famille="donnée brute", titre="Médiane d'une distribution",
            tige=f"Le même diagramme ci-contre ({ctx[1]}, {N} {ctx[2]} observés) doit être résumé par sa médiane dans un rapport d'activité. "
                 f"En classant les {N} observations par ordre croissant, quelle est la médiane de la série ?",
            bonne=fmt(med), faux=[fmt(mode) if mode != med else fmt(med + 1), fmt(moy, 2) if fmt(moy, 2) != fmt(med) else fmt(med + 2), fmt((vals[0] + vals[-1]) / 2) if fmt((vals[0] + vals[-1]) / 2) not in (fmt(med), fmt(mode)) else fmt(med - 1), fmt(N // 2)],
            correction=f"Effectifs cumulés : {', '.join(str(sum(eff[:i + 1])) for i in range(len(eff)))}. La moitié de N vaut {N / 2:g} ; la première valeur dont l'effectif cumulé atteint {N / 2:g} est {med} : médiane = {med}.",
            erreurs=["mode (bâton le plus haut) pris pour la médiane", "moyenne prise pour la médiane", "milieu de l'étendue", "rang N/2 confondu avec la valeur"], figure=fig, legende=leg, rnd=rnd)
    seuil = rnd.choice([v for v in vals if v > vals[0]])
    part = 100 * sum(e for v, e in zip(vals, eff) if v >= seuil) / N
    ajouter(id_=f"FIG2-MA-bat-{k}-3", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Fréquence cumulée et prise de décision à partir d'un diagramme", famille="décision professionnelle", titre="Décision à partir d'une distribution",
            tige=f"Le responsable {ctx[0]} décide d'intervenir si au moins la moitié des {ctx[2]} présentent {seuil} {ctx[1].split(' par')[0]} ou plus (diagramme ci-contre, {N} {ctx[2]} observés). Que doit-il conclure, et pourquoi ?",
            bonne=(f"Intervenir, car {sum(e for v, e in zip(vals, eff) if v >= seuil)} {ctx[2]} sur {N}, soit {fmt(part, 0)} %, atteignent le seuil" if part >= 50 else
                   f"Ne pas intervenir, car seuls {sum(e for v, e in zip(vals, eff) if v >= seuil)} {ctx[2]} sur {N}, soit {fmt(part, 0)} %, atteignent le seuil"),
            faux=[(f"Ne pas intervenir, car la moyenne {fmt(moy, 2)} est inférieure à {seuil}" if moy < seuil else f"Intervenir, car la moyenne {fmt(moy, 2)} dépasse {seuil}") if (moy < seuil) == (part >= 50) else (f"Intervenir, car le mode {mode} dépasse le seuil" if part < 50 else f"Ne pas intervenir, car le mode {mode} est sous le seuil"),
                  f"Intervenir, car {len([v for v in vals if v >= seuil])} valeurs sur {len(vals)} atteignent le seuil", f"Ne pas intervenir, car le bâton de {seuil} n'est pas le plus haut",
                  f"Intervenir, car la médiane {med} est {'supérieure' if med >= seuil else 'inférieure'} au seuil" if (med >= seuil) != (part >= 50) else f"Ne pas intervenir, car {eff[vals.index(seuil)]} {ctx[2]} seulement ont exactement {seuil}"],
            correction=f"Effectif des {ctx[2]} à {seuil} ou plus : {' + '.join(str(e) for v, e in zip(vals, eff) if v >= seuil)} = {sum(e for v, e in zip(vals, eff) if v >= seuil)}, soit {fmt(part, 0)} % de {N} : "
                       f"{'au moins' if part >= 50 else 'moins de'} la moitié, donc {'intervention' if part >= 50 else 'pas d intervention'}. La moyenne ou le mode ne répondent pas à la question posée (part des {ctx[2]} au-dessus du seuil).",
            erreurs=["moyenne utilisée au lieu de la proportion", "valeurs comptées au lieu des effectifs", "hauteur d'un seul bâton", "médiane ou effectif exact confondus avec la proportion"], figure=fig, legende=leg, rnd=rnd)


def m_aire(rnd: random.Random, k: int):
    """Aire sous une parabole y = a − x²/b (entre ses zéros) ; volume de révolution ; décision (quantité de matière)."""
    a = rnd.choice([2, 3, 4]); b = rnd.choice([1, 2, 4])
    r = math.sqrt(a * b)  # zéros ±r
    f = lambda x: a - x * x / b
    aire = 2 * (a * r - r ** 3 / (3 * b))
    vol = math.pi * 2 * (a * a * r - 2 * a * r ** 3 / (3 * b) + r ** 5 / (5 * b * b))
    p = Plot(-r - 1, r + 1, -1, a + 1, 440, 300, xstep=1, ystep=1)
    p.area(f, -r, r); p.curve(f, -r - 1, r + 1)
    p.label(0.2, a + 0.3, f"y = {a} − x²/{b}" if b != 1 else f"y = {a} − x²", NUIT, 13, "start", italic=True)
    fig, leg = p.render(), f"Région limitée par la parabole et l'axe des abscisses (unité : 1 dm)"
    ctx = rnd.choice([("Un ferblantier découpe une plaque", "tôle"), ("Un vitrier taille un vitrail", "verre"), ("Un menuisier dessine un fronton", "bois"), ("Un soudeur prépare une pièce", "acier")])
    ajouter(id_=f"FIG2-MA-aire-{k}-1", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chapitre("Mathématiques", "intégration", "primitives"), difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Aire d'un domaine sous une parabole par l'intégrale définie", famille="objet technique", titre="Aire d'une pièce parabolique",
            tige=f"{ctx[0]} dont le contour est la région colorée ci-contre, limitée par la parabole y = {a} − x²/{b} et l'axe des abscisses (1 unité = 1 dm). "
                 f"Quelle est l'aire exacte de cette pièce, en dm² ?",
            bonne=fmt(aire, 2), faux=[fmt(aire / 2, 2), fmt(2 * r * a, 2), fmt(aire * 1.5, 2), fmt(a * r, 2)],
            correction=f"Zéros : x = ±√({a}·{b}) = ±{fmt(r, 2)}. Aire = ∫ de −{fmt(r, 2)} à {fmt(r, 2)} de ({a} − x²/{b}) dx = 2[{a}x − x³/{3 * b}] de 0 à {fmt(r, 2)} = {fmt(aire, 2)} dm² (soit les deux tiers du rectangle {fmt(2 * r, 2)} × {a}).",
            erreurs=["intégrale sur une moitié seulement", "aire du rectangle englobant", "erreur de primitive (x³/b au lieu de x³/3b)", "demi-rectangle"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-MA-aire-{k}-2", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chapitre("Mathématiques", "géométriques", "intégrale"), difficulte="difficile", type_item="classique", competence="modéliser",
            savoir="Volume d'un solide de révolution V = π∫f²", famille="objet technique", titre="Volume engendré par la région",
            tige=f"Un tourneur fait tourner la région colorée ci-contre (sous y = {a} − x²/{b}, entre ses deux zéros, unité 1 dm) autour de l'axe des abscisses pour obtenir une pièce pleine. "
                 f"Quel est, arrondi au dixième, le volume de la pièce en dm³ ?",
            bonne=fmt(vol, 1), faux=[fmt(math.pi * aire, 1), fmt(vol / 2, 1), fmt(2 * math.pi * aire, 1), fmt(aire, 1)],
            correction=f"V = π∫ f(x)² dx = π∫({a} − x²/{b})² dx de −{fmt(r, 2)} à {fmt(r, 2)} = 2π[{a}²x − 2·{a}x³/(3·{b}) + x⁵/(5·{b}²)] de 0 à {fmt(r, 2)} ≈ {fmt(vol, 1)} dm³.",
            erreurs=["π × aire (oubli du carré de f)", "volume d'une moitié", "2π × aire", "aire donnée pour un volume"], figure=fig, legende=leg, rnd=rnd)
    ep = rnd.choice([2, 3, 5]); masse_v = rnd.choice([7.8, 2.5, 0.7])  # kg/dm³ : acier, verre, bois
    masse = aire * ep / 10 * masse_v
    limite = rnd.choice([5, 10, 20, 50])
    ajouter(id_=f"FIG2-MA-aire-{k}-3", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chapitre("Mathématiques", "géométriques", "intégrale"), difficulte="difficile", type_item="decision", competence="décider",
            savoir="Aire par intégrale puis masse d'une pièce : décision de manutention", famille="décision professionnelle", titre="Peut-on porter la pièce seul ?",
            tige=f"La pièce ci-contre (région sous y = {a} − x²/{b}, unité 1 dm) a une épaisseur de {ep} cm et une masse volumique de {fmt(masse_v)} kg/dm³. "
                 f"La consigne de sécurité de l'atelier interdit de porter seul plus de {limite} kg. Que doit faire l'ouvrier, et pourquoi ?",
            bonne=(f"Il peut la porter seul, car sa masse vaut environ {fmt(masse, 1)} kg, inférieure à {limite} kg" if masse <= limite else f"Il doit se faire aider, car sa masse vaut environ {fmt(masse, 1)} kg, supérieure à {limite} kg"),
            faux=[f"{'Il doit se faire aider' if masse <= limite else 'Il peut la porter seul'}, car l'aire {fmt(aire, 1)} dm² {'dépasse' if aire > limite else 'est sous'} {limite}",
                  f"{'Il peut la porter seul' if aire * ep * masse_v <= limite else 'Il doit se faire aider'}, car la masse vaut {fmt(aire * ep * masse_v, 1)} kg (épaisseur comptée en dm)",
                  f"Il peut la porter seul, car le volume {fmt(aire * ep / 10, 2)} dm³ est petit", f"Il doit se faire aider, car {fmt(2 * r * a, 1)} dm² × {ep} cm donne plus de {limite} kg"],
            correction=f"Volume = aire × épaisseur = {fmt(aire, 2)} dm² × {fmt(ep / 10, 1)} dm = {fmt(aire * ep / 10, 2)} dm³ ; masse = {fmt(aire * ep / 10, 2)} × {fmt(masse_v)} ≈ {fmt(masse, 1)} kg, {'inférieure' if masse <= limite else 'supérieure'} à {limite} kg.",
            erreurs=["aire comparée à une masse", "épaisseur non convertie en dm", "volume sans la masse volumique", "rectangle englobant au lieu de l'aire exacte"], figure=fig, legende=leg, rnd=rnd)


def m_arbre(rnd: random.Random, k: int):
    pA = rnd.choice([0.3, 0.4, 0.6, 0.7]); rA = rnd.choice([0.8, 0.9, 0.95]); rB = rnd.choice([0.5, 0.6, 0.7, 0.75])
    ctx = rnd.choice([("fournisseur A", "fournisseur B", "pièce conforme", "pièce défectueuse", "Une quincaillerie reçoit des pièces de deux fournisseurs"),
                      ("route goudronnée", "piste", "livraison à l'heure", "livraison en retard", "Un transporteur de Kikwit livre par deux itinéraires"),
                      ("semence certifiée", "semence locale", "levée réussie", "levée échouée", "Une coopérative agricole sème deux types de semences"),
                      ("réseau A", "réseau B", "appel réussi", "appel échoué", "Une radio communautaire relaie ses reportages par téléphone")])
    maj = lambda t: t[0].upper() + t[1:]
    fig = tree([(maj(ctx[0]), fmt(pA), [(maj(ctx[2]), fmt(rA)), (maj(ctx[3]), fmt(round(1 - rA, 2)))]), (maj(ctx[1]), fmt(round(1 - pA, 2)), [(maj(ctx[2]), fmt(rB)), (maj(ctx[3]), fmt(round(1 - rB, 2)))])])
    leg = "Arbre pondéré : origine puis résultat"
    tot = pA * rA + (1 - pA) * rB
    bayes = pA * rA / tot
    chap = chapitre("Mathématiques", "probabilités")
    ajouter(id_=f"FIG2-MA-arb-{k}-1", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Formule des probabilités totales sur un arbre pondéré", famille="document technique", titre="Probabilité totale sur un arbre",
            tige=f"{ctx[4]} ; l'arbre pondéré ci-contre donne la part de chaque origine puis la probabilité de réussite selon l'origine. "
                 f"Un cas est pris au hasard. Quelle est la probabilité d'obtenir « {ctx[2]} » ?",
            bonne=fmt(tot, 3), faux=[fmt(pA * rA, 3), fmt((rA + rB) / 2, 3), fmt(rA + rB, 3) if rA + rB < 1 else fmt(rA * rB, 3), fmt((1 - pA) * rB, 3)],
            correction=f"P = P(A)·P(réussite|A) + P(B)·P(réussite|B) = {fmt(pA)}×{fmt(rA)} + {fmt(1 - pA)}×{fmt(rB)} = {fmt(pA * rA, 3)} + {fmt((1 - pA) * rB, 3)} = {fmt(tot, 3)}.",
            erreurs=["une seule branche", "moyenne non pondérée", "somme ou produit des conditionnelles", "seconde branche seule"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-MA-arb-{k}-2", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="difficile", type_item="classique", competence="raisonner",
            savoir="Probabilité conditionnelle inversée (formule de Bayes) sur un arbre", famille="document technique", titre="Remonter l'arbre : probabilité a posteriori",
            tige=f"Avec l'arbre ci-contre ({ctx[4].lower()}), on apprend qu'un cas pris au hasard a donné « {ctx[2]} ». "
                 f"Quelle est la probabilité, arrondie au centième, qu'il provienne de l'origine « {ctx[0]} » ?",
            bonne=fmt(bayes, 2), faux=[fmt(rA, 2), fmt(pA, 2), fmt(pA * rA, 2), fmt(1 - bayes, 2)],
            correction=f"P(A|réussite) = P(A ∩ réussite)/P(réussite) = ({fmt(pA)}×{fmt(rA)})/{fmt(tot, 3)} = {fmt(pA * rA, 3)}/{fmt(tot, 3)} ≈ {fmt(bayes, 2)}.",
            erreurs=["conditionnelle lue dans le mauvais sens", "probabilité a priori de A", "probabilité de l'intersection sans diviser", "événement complémentaire"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-MA-arb-{k}-3", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Comparaison de probabilités conditionnelles pour choisir", famille="décision professionnelle", titre="Quelle origine privilégier ?",
            tige=f"{ctx[4]} (arbre ci-contre). Le gérant veut ne garder qu'une origine, celle qui donne le plus souvent « {ctx[2]} », à condition qu'elle réussisse plus de {fmt(100 * max(rA, rB) - 5, 0)} % du temps. Que doit-il décider, et pourquoi ?",
            bonne=f"Garder « {ctx[0] if rA > rB else ctx[1]} », car sa probabilité de réussite {fmt(max(rA, rB))} dépasse {fmt(min(rA, rB))} et le seuil",
            faux=[f"Garder « {ctx[0] if pA > 0.5 else ctx[1]} », car c'est l'origine la plus fréquente ({fmt(max(pA, 1 - pA))})", f"Garder « {ctx[1] if rA > rB else ctx[0]} », car {fmt(pA * rA if rA < rB else (1 - pA) * rB)} est la plus grande probabilité de l'arbre",
                  f"Ne rien changer, car la probabilité globale {fmt(tot, 2)} est acceptable", f"Garder les deux, car {fmt(rA)} et {fmt(rB)} se compensent"],
            correction=f"Il faut comparer les probabilités conditionnelles de réussite : {fmt(rA)} pour « {ctx[0]} » et {fmt(rB)} pour « {ctx[1]} » ; la plus grande est {fmt(max(rA, rB))}, au-dessus du seuil. La fréquence d'origine ({fmt(pA)}) ne mesure pas la qualité.",
            erreurs=["fréquence d'origine confondue avec qualité", "probabilité d'intersection confondue avec conditionnelle", "probabilité globale sans comparaison", "aucune décision"], figure=fig, legende=leg, rnd=rnd)


def m_complexe(rnd: random.Random, k: int):
    x, y = rnd.choice([(3, 4), (4, 3), (6, 8), (-3, 4), (5, 12), (-6, 8), (8, 6), (1, 2), (2, 5), (-2, 3), (3, 1), (-4, 3)])
    mod = math.hypot(x, y); arg = math.degrees(math.atan2(y, x))
    p = Plot(min(-1, x - 2), max(x + 2, 3), min(-1, y - 2), max(y + 2, 3), 360, 320, xstep=1 if max(abs(x), abs(y)) <= 6 else 2, ystep=1 if max(abs(x), abs(y)) <= 6 else 2, xlabel="Re", ylabel="Im")
    p.segment(0, 0, x, y, NUIT, 2, arrow=True); p.dashes_to_axes(x, y); p.point(x, y, "M", dx=8, dy=-6)
    fig, leg = p.render(), "Image M du nombre complexe z"
    chap = chapitre("Mathématiques", "complexes")
    ctx = rnd.choice(["Sur le plan d'un installateur d'antennes", "Sur l'écran radar du port de Matadi", "Sur le relevé d'un géomètre", "Sur le schéma d'un bras de grue"])
    ajouter(id_=f"FIG2-MA-cpx-{k}-1", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Module d'un nombre complexe à partir de son image", famille="document graphique", titre="Module lu sur une figure",
            tige=f"{ctx}, le point M est l'image du nombre complexe z dans un repère orthonormé (1 unité = 100 m) ; ses coordonnées se lisent sur la figure ci-contre. Quelle est la distance OM, en mètres ?",
            bonne=f"{fmt(mod * 100, 0)}", faux=[f"{fmt((abs(x) + abs(y)) * 100, 0)}", f"{fmt(mod * mod * 100, 0)}" if mod * mod != mod else f"{fmt(abs(x) * 100, 0)}", f"{fmt(abs(x * y) * 100, 0)}" if abs(x * y) != mod else f"{fmt(abs(y) * 100, 0)}", f"{fmt(mod * 10, 0)}"],
            correction=f"z = {x} {'+' if y >= 0 else '−'} {abs(y)}i ; |z| = √({x}² + {y}²) = √{x * x + y * y} = {fmt(mod, 2)} unités, soit {fmt(mod * 100, 0)} m.",
            erreurs=["somme des valeurs absolues", "carré du module", "produit des coordonnées", "erreur d'échelle"], figure=fig, legende=leg, rnd=rnd)
    argp = {45: "π/4", 135: "3π/4", 90: "π/2", 0: "0"}.get(round(arg), None)
    ajouter(id_=f"FIG2-MA-cpx-{k}-2", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="moyen", type_item="classique", competence="raisonner",
            savoir="Conjugué, opposé, multiplication par i : interprétation géométrique", famille="document graphique", titre="Image de i·z",
            tige=f"Le point M d'affixe z = {x} {'+' if y >= 0 else '−'} {abs(y)}i est placé ci-contre. On fait tourner M d'un quart de tour dans le sens direct autour de O, ce qui revient à multiplier z par i. Quelle est l'affixe du point obtenu ?",
            bonne=f"{fmt(-y)} {'+' if x >= 0 else '−'} {abs(x)}i", faux=[f"{fmt(y)} {'+' if -x >= 0 else '−'} {abs(x)}i", f"{x} {'+' if -y >= 0 else '−'} {abs(y)}i", f"{fmt(-x)} {'+' if -y >= 0 else '−'} {abs(y)}i", f"{fmt(-y)} {'+' if -x >= 0 else '−'} {abs(x)}i"],
            correction=f"i·z = i({x} {'+' if y >= 0 else '−'} {abs(y)}i) = {x}i + {y}i² = {fmt(-y)} {'+' if x >= 0 else '−'} {abs(x)}i. Géométriquement, (x ; y) devient (−y ; x).",
            erreurs=["rotation dans le sens indirect (−i·z)", "conjugué de z", "opposé de z", "signes mal gérés avec i² = −1"], figure=fig, legende=leg, rnd=rnd)
    portee = rnd.choice([400, 500, 800, 1000, 1300])
    ajouter(id_=f"FIG2-MA-cpx-{k}-3", discipline="Mathématiques", sous=None, epreuve="M.46", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Module d'un complexe et comparaison à une distance limite", famille="décision professionnelle", titre="À portée ou hors de portée ?",
            tige=f"{ctx}, l'émetteur est en O et le point M (figure ci-contre, 1 unité = 100 m) est l'image de z = {x} {'+' if y >= 0 else '−'} {abs(y)}i. La portée garantie de l'appareil est de {portee} m. "
                 f"L'installateur doit-il prévoir un relais, et pourquoi ?",
            bonne=(f"Non, car OM = |z| = {fmt(mod * 100, 0)} m, inférieure à la portée de {portee} m" if mod * 100 <= portee else f"Oui, car OM = |z| = {fmt(mod * 100, 0)} m, supérieure à la portée de {portee} m"),
            faux=[(f"Oui, car {abs(x)} + {abs(y)} = {abs(x) + abs(y)} unités donnent {(abs(x) + abs(y)) * 100} m, au-delà de {portee} m" if (abs(x) + abs(y)) * 100 > portee else f"Non, car {abs(x)} + {abs(y)} = {abs(x) + abs(y)} unités donnent {(abs(x) + abs(y)) * 100} m, sous {portee} m"),
                  f"{'Oui' if abs(x) * 100 > portee else 'Non'}, car seule l'abscisse {abs(x)} compte, soit {abs(x) * 100} m", f"Oui, car {x * x + y * y} unités² dépassent {portee}", f"Non, car l'argument de z ne dépasse pas 90°"],
            correction=f"La distance OM est le module |z| = √({x}² + {y}²) = {fmt(mod, 2)} unités = {fmt(mod * 100, 0)} m, à comparer à {portee} m.",
            erreurs=["distance de Manhattan au lieu du module", "une seule coordonnée", "carré du module", "argument hors sujet"], figure=fig, legende=leg, rnd=rnd)


# ======================================================================================================================
# PHYSIQUE
# ======================================================================================================================

def p_vt(rnd: random.Random, k: int):
    t1 = rnd.choice([2, 3, 4, 5]); t2 = t1 + rnd.choice([4, 6, 8]); t3 = t2 + rnd.choice([2, 3, 4]); v = rnd.choice([8, 10, 12, 15, 20])
    p = Plot(0, t3 + 2, 0, v + 4, 460, 300, xstep=2 if t3 > 10 else 1, ystep=2 if v <= 12 else 5, xlabel="t (s)", ylabel="v (m/s)")
    p.area(lambda t: v * t / t1 if t <= t1 else (v if t <= t2 else v * (t3 - t) / (t3 - t2)), 0, t3, OR, 0.22)
    p.polyline([(0, 0), (t1, v), (t2, v), (t3, 0)], NUIT, 2.4)
    fig, leg = p.render(), "Vitesse en fonction du temps"
    d = 0.5 * t1 * v + (t2 - t1) * v + 0.5 * (t3 - t2) * v
    acc = v / t1; dec = v / (t3 - t2)
    veh = rnd.choice(["une moto-taxi", "un bus de la ligne Matadi–Boma", "un wagonnet de mine", "un camion de la cimenterie", "une pirogue motorisée"])
    veh_de = "d'" + veh.split(" ", 1)[1] if veh.startswith("un ") or veh.startswith("une ") else "de " + veh
    veh_de = ("d'un " if veh.startswith("un ") else "d'une ") + veh.split(" ", 1)[1]
    chap = chapitre("Physique", "cinématique")
    ajouter(id_=f"FIG2-PH-vt-{k}-1", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="interpréter",
            savoir="Distance parcourue = aire sous le diagramme v(t)", famille="donnée brute", titre="Distance lue sur un diagramme des vitesses",
            tige=f"L'enregistreur embarqué sur {veh} a tracé la vitesse en fonction du temps entre deux arrêts (figure) : accélération, palier, freinage. Quelle distance a été parcourue entre le départ et l'arrêt ?",
            bonne=f"{fmt(d)} m", faux=[f"{fmt(v * t3)} m", f"{fmt((t2 - t1) * v)} m", f"{fmt(d + 0.5 * t1 * v)} m", f"{fmt(v * t2)} m"],
            correction=f"Aire sous v(t) : triangle ½×{t1}×{v} = {fmt(0.5 * t1 * v)} m ; rectangle ({t2}−{t1})×{v} = {fmt((t2 - t1) * v)} m ; triangle ½×{t3 - t2}×{v} = {fmt(0.5 * (t3 - t2) * v)} m. Total {fmt(d)} m.",
            erreurs=["v_max × durée totale", "palier seulement", "premier triangle compté deux fois", "v_max × t₂"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-PH-vt-{k}-2", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Accélération = pente du diagramme v(t)", famille="donnée brute", titre="Accélération au démarrage",
            tige=f"Sur le diagramme v(t) ci-contre {veh_de}, la vitesse passe de 0 à {v} m/s pendant les {t1} premières secondes, puis reste constante avant le freinage. Quelle est l'accélération pendant la phase de démarrage ?",
            bonne=f"{fmt(acc, 2)} m/s²", faux=[f"{fmt(v, 2)} m/s²", f"{fmt(t1 / v, 2)} m/s²", f"{fmt(dec, 2)} m/s²" if fmt(dec, 2) != fmt(acc, 2) else f"{fmt(acc * 2, 2)} m/s²", f"{fmt(v * t1, 2)} m/s²"],
            correction=f"a = Δv/Δt = {v}/{t1} = {fmt(acc, 2)} m/s² (pente du premier segment). Sur le palier, a = 0 ; au freinage, a = −{fmt(dec, 2)} m/s².",
            erreurs=["vitesse prise pour accélération", "rapport inversé", "décélération du freinage", "produit v×t"], figure=fig, legende=leg, rnd=rnd)
    lim = rnd.choice([d - 20, d + 20, d - 50, d + 50]); lim = max(10, round(lim / 10) * 10)
    ajouter(id_=f"FIG2-PH-vt-{k}-3", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Distance d'arrêt lue sur v(t) et décision de sécurité", famille="décision professionnelle", titre="La manœuvre tient-elle dans la distance disponible ?",
            tige=f"Le conducteur {veh_de} dispose de {lim} m entre le point de départ et une barrière. Le diagramme v(t) ci-contre décrit la manœuvre complète qu'il prévoit (démarrage, palier, freinage jusqu'à l'arrêt). Que doit-il conclure, et pourquoi ?",
            bonne=(f"La manœuvre est possible, car la distance parcourue, aire sous la courbe, vaut {fmt(d)} m, inférieure à {lim} m" if d <= lim else f"Il doit réduire le palier, car la distance parcourue, aire sous la courbe, vaut {fmt(d)} m, supérieure à {lim} m"),
            faux=[(f"Il doit réduire le palier, car {v} m/s × {t3} s = {fmt(v * t3)} m dépassent {lim} m" if v * t3 > lim else f"La manœuvre est possible, car {v} m/s × {t3} s = {fmt(v * t3)} m restent sous {lim} m"),
                  f"La manœuvre est possible, car la vitesse {v} m/s est inférieure à {lim}", f"Il doit réduire le palier, car le freinage dure {t3 - t2} s", f"La manœuvre est possible, car le palier ne fait que {fmt((t2 - t1) * v)} m"],
            correction=f"La distance parcourue est l'aire sous v(t) : {fmt(d)} m. Comparée à {lim} m, elle est {'inférieure' if d <= lim else 'supérieure'} : {'manœuvre possible' if d <= lim else 'il faut raccourcir le palier'}. Multiplier v_max par la durée totale surestime la distance.",
            erreurs=["v_max × durée totale", "vitesse comparée à une distance", "durée du freinage sans calcul", "palier seul"], figure=fig, legende=leg, rnd=rnd)


def p_circuit(rnd: random.Random, k: int):
    U = rnd.choice([6, 9, 12, 24]); R1 = rnd.choice([2, 3, 4, 6, 8]); R2 = rnd.choice([2, 4, 6, 10, 12])
    I = U / (R1 + R2); U1 = R1 * I; P2 = R2 * I * I
    fig = circuit_serie([("R", f"R₁ = {R1} Ω"), ("R", f"R₂ = {R2} Ω")], (f"U = {U} V",), [("A", "")])
    leg = "Deux résistances en série alimentées par une source continue"
    chap = chapitre("Physique", "courant", "alternatif") if "ohm" in chapitre("Physique", "ohm").lower() else chapitre("Physique", "alternatif")
    ctx = rnd.choice(["le tableau de bord d'un camion", "un circuit d'éclairage de pirogue", "une armoire de commande de scierie", "le ballast d'une lampe de dispensaire"])
    ajouter(id_=f"FIG2-PH-cir-{k}-1", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Loi d'Ohm dans un circuit série : résistance équivalente et intensité", famille="document technique", titre="Intensité dans un circuit série",
            tige=f"Le schéma ci-contre, relevé sur {ctx}, montre deux résistances R₁ = {R1} Ω et R₂ = {R2} Ω en série sous une tension continue U = {U} V. Quelle intensité l'ampèremètre indique-t-il ?",
            bonne=f"{fmt(I, 2)} A", faux=[f"{fmt(U / R1, 2)} A", f"{fmt(U / R2, 2)} A", f"{fmt(U * (R1 + R2), 2)} A", f"{fmt(U / (R1 * R2 / (R1 + R2)), 2)} A"],
            correction=f"En série, R_eq = R₁ + R₂ = {R1 + R2} Ω ; I = U/R_eq = {U}/{R1 + R2} = {fmt(I, 2)} A.",
            erreurs=["R₁ seule", "R₂ seule", "U × R au lieu de U/R", "résistances traitées en parallèle"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-PH-cir-{k}-2", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Diviseur de tension : tension aux bornes d'une résistance en série", famille="document technique", titre="Tension aux bornes de R₁",
            tige=f"Dans le circuit série ci-contre (U = {U} V, R₁ = {R1} Ω, R₂ = {R2} Ω), un technicien veut brancher un voltmètre aux bornes de R₁. Quelle tension doit-il lire ?",
            bonne=f"{fmt(U1, 2)} V", faux=[f"{fmt(U - U1, 2)} V", f"{fmt(U, 2)} V", f"{fmt(U / 2, 2)} V" if fmt(U / 2, 2) not in (fmt(U1, 2), fmt(U - U1, 2)) else f"{fmt(U1 * 2, 2)} V", f"{fmt(R1 / U, 2)} V"],
            correction=f"U₁ = R₁·I = {R1} × {fmt(I, 2)} = {fmt(U1, 2)} V (ou U·R₁/(R₁+R₂) = {U}×{R1}/{R1 + R2}). On vérifie U₁ + U₂ = {fmt(U1, 2)} + {fmt(U - U1, 2)} = {U} V.",
            erreurs=["tension aux bornes de R₂", "tension totale", "partage en deux moitiés", "rapport inversé"], figure=fig, legende=leg, rnd=rnd)
    pmax = rnd.choice([0.5, 1, 2, 5, 10])
    ajouter(id_=f"FIG2-PH-cir-{k}-3", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Puissance dissipée P = R·I² et choix d'une résistance", famille="décision professionnelle", titre="La résistance va-t-elle chauffer ?",
            tige=f"Sur {ctx} (schéma ci-contre, U = {U} V, R₁ = {R1} Ω, R₂ = {R2} Ω), la résistance R₂ disponible au magasin est prévue pour {fmt(pmax)} W au maximum. Le technicien peut-il la monter, et pourquoi ?",
            bonne=(f"Oui, car R₂ dissipe R₂·I² = {fmt(P2, 2)} W, moins que {fmt(pmax)} W" if P2 <= pmax else f"Non, car R₂ dissipe R₂·I² = {fmt(P2, 2)} W, plus que {fmt(pmax)} W"),
            faux=[(f"Non, car U·I = {fmt(U * I, 2)} W dépasse {fmt(pmax)} W" if U * I > pmax else f"Oui, car U·I = {fmt(U * I, 2)} W reste sous {fmt(pmax)} W") if (U * I > pmax) != (P2 > pmax) else (f"Non, car U²/R₂ = {fmt(U * U / R2, 2)} W dépasse {fmt(pmax)} W" if U * U / R2 > pmax else f"Oui, car U²/R₂ = {fmt(U * U / R2, 2)} W reste sous {fmt(pmax)} W"),
                  f"Oui, car l'intensité {fmt(I, 2)} A est inférieure à {fmt(pmax)}", f"Non, car {U} V dépassent {fmt(pmax)} W", f"Oui, car en série la puissance se partage à parts égales : {fmt(U * I / 2, 2)} W"],
            correction=f"I = {fmt(I, 2)} A ; P₂ = R₂·I² = {R2} × {fmt(I, 2)}² = {fmt(P2, 2)} W, {'inférieure' if P2 <= pmax else 'supérieure'} à {fmt(pmax)} W. U·I est la puissance totale, U²/R₂ supposerait R₂ seule sous U.",
            erreurs=["puissance totale ou U²/R₂ au lieu de R₂·I²", "intensité comparée à une puissance", "tension comparée à une puissance", "partage égal supposé"], figure=fig, legende=leg, rnd=rnd)


def p_incline(rnd: random.Random, k: int):
    m = rnd.choice([10, 15, 20, 25, 40, 50]); ang = rnd.choice([15, 20, 25, 30, 35, 40, 45]); g = 10
    P = m * g; Fp = P * math.sin(math.radians(ang)); Fn = P * math.cos(math.radians(ang))
    fig = plan_incline(ang, [("P", -90, 80, ROUGE), ("R", 90 + ang, 70, VERT)], masse_label=f"{m} kg")
    leg = f"Charge de {m} kg sur un plan incliné de {ang}°"
    chap = chapitre("Physique", "plan incliné", "poids")
    ctx = rnd.choice(["un fût de carburant", "un sac de ciment", "une caisse de pièces", "un wagonnet de minerai"])
    ajouter(id_=f"FIG2-PH-inc-{k}-1", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Composante du poids parallèle au plan incliné : P·sin α", famille="scène de travail", titre="Force pour retenir la charge",
            tige=f"Un manutentionnaire retient {ctx} ({m} kg) sur un plan incliné de {ang}°, sans frottement (figure : poids P et réaction R). On prend g = 10 N/kg. Quelle force parallèle à la pente doit-il exercer au minimum pour l'empêcher de glisser ?",
            bonne=f"{fmt(Fp, 0)} N", faux=[f"{fmt(Fn, 0)} N", f"{fmt(P, 0)} N", f"{fmt(m * math.sin(math.radians(ang)), 1)} N", f"{fmt(P * math.tan(math.radians(ang)), 0)} N"],
            correction=f"P = mg = {m}×10 = {P} N. Composante parallèle : P·sin {ang}° = {P} × {fmt(math.sin(math.radians(ang)), 3)} ≈ {fmt(Fp, 0)} N. La composante normale P·cos {ang}° ≈ {fmt(Fn, 0)} N est compensée par R.",
            erreurs=["composante normale (cos)", "poids entier", "masse au lieu du poids", "tangente au lieu du sinus"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-PH-inc-{k}-2", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Réaction normale du plan : R = P·cos α", famille="scène de travail", titre="Réaction du plan incliné",
            tige=f"Pour {ctx} de {m} kg posé sur la pente de {ang}° (figure ci-contre, g = 10 N/kg, pas de frottement), quelle est la valeur de la réaction R du plan sur la charge ?",
            bonne=f"{fmt(Fn, 0)} N", faux=[f"{fmt(Fp, 0)} N", f"{fmt(P, 0)} N", f"{fmt(P / math.cos(math.radians(ang)), 0)} N", f"{fmt(m * math.cos(math.radians(ang)), 1)} N"],
            correction=f"R équilibre la composante normale du poids : R = P·cos {ang}° = {P} × {fmt(math.cos(math.radians(ang)), 3)} ≈ {fmt(Fn, 0)} N.",
            erreurs=["composante parallèle", "poids entier", "division par cos au lieu de multiplier", "masse au lieu du poids"], figure=fig, legende=leg, rnd=rnd)
    fmax = rnd.choice([100, 150, 200, 250, 300])
    ajouter(id_=f"FIG2-PH-inc-{k}-3", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Comparaison de la composante du poids à une force disponible", famille="décision professionnelle", titre="Seul ou à deux ?",
            tige=f"Un ouvrier peut exercer au plus {fmax} N le long d'une pente. Il doit retenir {ctx} de {m} kg sur le plan incliné de {ang}° (figure, g = 10 N/kg, sans frottement). Que doit-il décider, et pourquoi ?",
            bonne=(f"Il peut retenir seul, car la composante du poids le long de la pente vaut P·sin {ang}° ≈ {fmt(Fp, 0)} N, inférieure à {fmax} N" if Fp <= fmax else f"Il doit se faire aider, car la composante du poids le long de la pente vaut P·sin {ang}° ≈ {fmt(Fp, 0)} N, supérieure à {fmax} N"),
            faux=[(f"Il doit se faire aider, car le poids {P} N dépasse {fmax} N" if P > fmax else f"Il peut retenir seul, car le poids {P} N reste sous {fmax} N") if (P > fmax) != (Fp > fmax) else (f"Il doit se faire aider, car P·cos {ang}° ≈ {fmt(Fn, 0)} N dépasse {fmax} N" if Fn > fmax else f"Il peut retenir seul, car P·cos {ang}° ≈ {fmt(Fn, 0)} N reste sous {fmax} N"),
                  f"Il peut retenir seul, car la masse {m} kg est inférieure à {fmax}", f"Il doit se faire aider, car la pente de {ang}° dépasse 10°", f"Il peut retenir seul, car la réaction R annule le poids"],
            correction=f"Seule la composante parallèle P·sin {ang}° = {P} × {fmt(math.sin(math.radians(ang)), 3)} ≈ {fmt(Fp, 0)} N est à retenir ; elle est {'inférieure' if Fp <= fmax else 'supérieure'} à {fmax} N.",
            erreurs=["poids entier ou composante normale", "masse comparée à une force", "angle seul sans calcul", "rôle de la réaction mal compris"], figure=fig, legende=leg, rnd=rnd)


def p_oscillo(rnd: random.Random, k: int):
    T = rnd.choice([0.2, 0.25, 0.4, 0.5, 0.8, 1.0]); A = rnd.choice([2, 3, 4, 5])
    p = Plot(0, 2.5 * T, -A - 1, A + 1, 460, 280, xstep=T / 2, ystep=1 if A <= 3 else 2, xlabel="t (s)", ylabel="x (cm)", xfmt=lambda v: fmt(round(v, 3), 3))
    p.curve(lambda t: A * math.cos(2 * math.pi * t / T))
    fig, leg = p.render(), "Déplacement x en fonction du temps"
    f = 1 / T; vmax = A / 100 * 2 * math.pi / T
    chap = chapitre("Physique", "oscillateurs", "pendules")
    ctx = rnd.choice(["le bâti d'une machine à coudre industrielle", "la membrane d'un haut-parleur de studio", "le flotteur d'une bouée du port", "la lame d'une scie à ruban"])
    ajouter(id_=f"FIG2-PH-osc-{k}-1", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="facile", type_item="classique", competence="interpréter",
            savoir="Période et fréquence lues sur un oscillogramme", famille="donnée brute", titre="Fréquence d'une vibration",
            tige=f"Un capteur fixé sur {ctx} enregistre son déplacement x au cours du temps (oscillogramme ci-contre). Le technicien doit noter la fréquence de vibration. Quelle est-elle ?",
            bonne=f"{fmt(f, 2)} Hz", faux=[f"{fmt(T, 2)} Hz", f"{fmt(A)} Hz", f"{fmt(2 * f, 2)} Hz", f"{fmt(f / 2, 2)} Hz"],
            correction=f"Un motif complet se répète toutes les {fmt(T, 2)} s : T = {fmt(T, 2)} s, donc f = 1/T = {fmt(f, 2)} Hz. L'amplitude ({A} cm) n'intervient pas.",
            erreurs=["période donnée pour la fréquence", "amplitude confondue avec la fréquence", "demi-période utilisée", "double période utilisée"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-PH-osc-{k}-2", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Vitesse maximale d'un oscillateur harmonique v_max = Aω", famille="donnée brute", titre="Vitesse maximale de l'oscillateur",
            tige=f"L'oscillogramme ci-contre ({ctx}) montre un mouvement sinusoïdal d'amplitude {A} cm et de période {fmt(T, 2)} s. Quelle est la vitesse maximale du point mesuré, arrondie au centième ?",
            bonne=f"{fmt(vmax, 2)} m/s", faux=[f"{fmt(A / 100 / T, 2)} m/s", f"{fmt(vmax * 100, 2)} m/s", f"{fmt(A / 100 * 2 * math.pi * T, 2)} m/s", f"{fmt(vmax / 2, 2)} m/s"],
            correction=f"ω = 2π/T = 2π/{fmt(T, 2)} ≈ {fmt(2 * math.pi / T, 2)} rad/s ; v_max = Aω = {A / 100} m × {fmt(2 * math.pi / T, 2)} ≈ {fmt(vmax, 2)} m/s.",
            erreurs=["A/T sans le facteur 2π", "amplitude laissée en cm", "T multiplié au lieu de divisé", "facteur ½ injustifié"], figure=fig, legende=leg, rnd=rnd)
    fres = rnd.choice([f * 0.5, f, f * 2, f * 1.1, f * 0.9]); fres = round(fres, 2)
    ajouter(id_=f"FIG2-PH-osc-{k}-3", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="difficile", type_item="decision", competence="décider",
            savoir="Résonance : coïncidence de fréquence d'excitation et de fréquence propre", famille="décision professionnelle", titre="Risque de résonance",
            tige=f"La fréquence propre du support de {ctx} vaut {fmt(fres, 2)} Hz. L'oscillogramme ci-contre montre la vibration imposée par le moteur (amplitude {A} cm). Le technicien doit-il craindre la résonance, et pourquoi ?",
            bonne=(f"Oui, car la fréquence imposée 1/T = {fmt(f, 2)} Hz coïncide avec la fréquence propre {fmt(fres, 2)} Hz" if abs(fres - f) < 0.01 else f"Non, car la fréquence imposée 1/T = {fmt(f, 2)} Hz diffère nettement de la fréquence propre {fmt(fres, 2)} Hz"),
            faux=[(f"Non, car la période {fmt(T, 2)} s diffère de {fmt(fres, 2)}" if abs(fres - f) < 0.01 else f"Oui, car la période {fmt(T, 2)} s est proche de {fmt(fres, 2)}"), f"Oui, car l'amplitude {A} cm est grande", f"Non, car la résonance exige une amplitude nulle au départ",
                  f"{'Non' if abs(fres - f) < 0.01 else 'Oui'}, car {fmt(f, 2)} Hz est {'différent' if abs(fres - f) < 0.01 else 'un multiple'} de {fmt(fres, 2)} Hz"],
            correction=f"Fréquence imposée f = 1/T = 1/{fmt(T, 2)} = {fmt(f, 2)} Hz ; fréquence propre {fmt(fres, 2)} Hz : {'égales, résonance à craindre' if abs(fres - f) < 0.01 else 'différentes, pas de résonance'}. La période ne se compare pas directement à une fréquence ; l'amplitude ne décide pas de la résonance.",
            erreurs=["période comparée à une fréquence", "amplitude prise pour critère", "condition inventée", "raisonnement inversé"], figure=fig, legende=leg, rnd=rnd)


def p_transfo(rnd: random.Random, k: int):
    N1 = rnd.choice([500, 1000, 2000, 1100]); N2 = rnd.choice([25, 50, 100, 200, 4400 // 2]); U1 = rnd.choice([220, 110, 380])
    if N2 > N1 and rnd.random() < 0.5:
        N1, N2 = N2, N1
    U2 = U1 * N2 / N1
    fig = transformateur(N1, N2, f"{U1} V"); leg = f"Transformateur : primaire {N1} spires, secondaire {N2} spires"
    chap = chapitre("Physique", "transformateur", "alternatif")
    app = rnd.choice(["un chargeur de radio", "une soudeuse à l'arc", "une sonnette de portail", "un poste à lampe UV de dispensaire"])
    app_de = "d'" + app[3:] if app.startswith("un ") else "d'" + app[4:]
    app_de = app_de.replace("d'", "d'un " if app.startswith("un ") else "d'une ")
    ajouter(id_=f"FIG2-PH-tra-{k}-1", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Transformateur parfait : U₂/U₁ = N₂/N₁", famille="objet technique", titre="Tension au secondaire",
            tige=f"Le schéma ci-contre est celui du transformateur, supposé parfait, {app_de} branché sur {U1} V. Les nombres de spires sont indiqués. Quelle tension efficace obtient-on au secondaire ?",
            bonne=f"{fmt(U2, 1)} V", faux=[f"{fmt(U1 * N1 / N2, 1)} V", f"{fmt(U2 * 2, 1)} V", f"{fmt(U1, 1)} V", f"{fmt(U2 / 2, 1)} V"],
            correction=f"U₂ = U₁ × N₂/N₁ = {U1} × {N2}/{N1} = {fmt(U2, 1)} V : transformateur {'abaisseur' if N2 < N1 else 'élévateur'}.",
            erreurs=["rapport inversé", "facteur 2 en trop", "tension inchangée", "facteur ½ en trop"], figure=fig, legende=leg, rnd=rnd)
    I2 = rnd.choice([0.5, 1, 2, 5, 10]); I1 = I2 * N2 / N1
    ajouter(id_=f"FIG2-PH-tra-{k}-2", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Conservation de la puissance : U₁I₁ = U₂I₂", famille="objet technique", titre="Intensité au primaire",
            tige=f"Le secondaire du transformateur ci-contre ({N1} et {N2} spires, U₁ = {U1} V) débite {fmt(I2)} A dans {app}. Le transformateur est supposé sans pertes. Quelle intensité le primaire absorbe-t-il ?",
            bonne=f"{fmt(I1, 3)} A", faux=[f"{fmt(I2 * N1 / N2, 3)} A", f"{fmt(I2, 3)} A", f"{fmt(U2 * I2 / U2 if U2 else 1, 3)} A" if fmt(U2 * I2 / U2, 3) != fmt(I1, 3) else f"{fmt(I1 * 10, 3)} A", f"{fmt(I1 / 2, 3)} A"],
            correction=f"Sans pertes, U₁I₁ = U₂I₂ ⇒ I₁ = I₂ × U₂/U₁ = I₂ × N₂/N₁ = {fmt(I2)} × {N2}/{N1} = {fmt(I1, 3)} A : l'intensité est {'plus faible' if I1 < I2 else 'plus forte'} au primaire quand la tension y est {'plus élevée' if U1 > U2 else 'plus faible'}.",
            erreurs=["rapport inversé", "intensité supposée conservée", "confusion U et I", "facteur ½ injustifié"], figure=fig, legende=leg, rnd=rnd)
    cal = rnd.choice([0.5, 1, 2, 3, 5])
    ajouter(id_=f"FIG2-PH-tra-{k}-3", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Choix d'un fusible au primaire d'un transformateur", famille="décision professionnelle", titre="Le fusible du primaire tiendra-t-il ?",
            tige=f"L'électricien protège le primaire du transformateur ci-contre ({N1}/{N2} spires, {U1} V) par un fusible de {fmt(cal)} A. L'appareil ({app}) tire {fmt(I2)} A au secondaire ; pertes négligées. Que doit-il conclure, et pourquoi ?",
            bonne=(f"Le fusible convient, car le primaire absorbe I₂·N₂/N₁ = {fmt(I1, 2)} A, moins que {fmt(cal)} A" if I1 <= cal else f"Le fusible fondra, car le primaire absorbe I₂·N₂/N₁ = {fmt(I1, 2)} A, plus que {fmt(cal)} A"),
            faux=[(f"Le fusible fondra, car {fmt(I2)} A dépassent {fmt(cal)} A" if I2 > cal else f"Le fusible convient, car {fmt(I2)} A restent sous {fmt(cal)} A") if (I2 > cal) != (I1 > cal) else (f"Le fusible fondra, car I₂·N₁/N₂ = {fmt(I2 * N1 / N2, 2)} A dépassent {fmt(cal)} A" if I2 * N1 / N2 > cal else f"Le fusible convient, car I₂·N₁/N₂ = {fmt(I2 * N1 / N2, 2)} A restent sous {fmt(cal)} A"),
                  f"Le fusible convient, car la tension {U1} V est bien supérieure à {fmt(cal)}", f"Le fusible fondra, car la puissance {fmt(U2 * I2, 0)} W dépasse {fmt(cal)}", f"Le fusible convient, car un transformateur ne consomme aucun courant au primaire"],
            correction=f"I₁ = I₂ × N₂/N₁ = {fmt(I2)} × {N2}/{N1} = {fmt(I1, 2)} A, {'inférieure' if I1 <= cal else 'supérieure'} au calibre {fmt(cal)} A. L'intensité du secondaire ne traverse pas le fusible du primaire.",
            erreurs=["intensité du secondaire ou rapport inversé", "tension comparée à une intensité", "puissance comparée à une intensité", "primaire supposé sans courant"], figure=fig, legende=leg, rnd=rnd)


def p_lentille(rnd: random.Random, k: int):
    f = rnd.choice([4, 5, 6, 8, 10]); do = rnd.choice([v for v in (1.5 * f, 2 * f, 2.5 * f, 3 * f, 1.25 * f) if v != f])
    di = 1 / (1 / f - 1 / do); gr = -di / do
    fig = lentille(f, do, 1.0); leg = f"Lentille convergente de distance focale {fmt(f)} cm, objet AB à {fmt(do)} cm"
    chap = chapitre("Physique", "optique", "ondes")
    ctx = rnd.choice(["un projecteur de cinéma ambulant", "une loupe de bijoutier", "l'objectif d'un appareil photo de studio", "un rétroprojecteur de salle de réunion"])
    ajouter(id_=f"FIG2-PH-len-{k}-1", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Relation de conjugaison 1/OA' − 1/OA = 1/f'", famille="objet technique", titre="Position de l'image",
            tige=f"La figure ci-contre montre {ctx} schématisé par une lentille convergente de distance focale {fmt(f)} cm ; l'objet AB est placé à {fmt(do)} cm devant la lentille. À quelle distance de la lentille se forme l'image A'B' ?",
            bonne=f"{fmt(di, 1)} cm", faux=[f"{fmt(do, 1)} cm", f"{fmt(f, 1)} cm", f"{fmt(do + f, 1)} cm", f"{fmt(do * f / (do + f), 1)} cm"],
            correction=f"1/OA' = 1/f' + 1/OA avec OA = −{fmt(do)} : 1/OA' = 1/{fmt(f)} − 1/{fmt(do)} ⇒ OA' = {fmt(di, 1)} cm (image réelle, derrière la lentille).",
            erreurs=["image supposée symétrique de l'objet", "image placée au foyer", "somme des distances", "signe faux dans la conjugaison"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-PH-len-{k}-2", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="interpréter",
            savoir="Grandissement γ = OA'/OA : taille et sens de l'image", famille="objet technique", titre="Grandissement de l'image",
            tige=f"Pour la lentille ci-contre (f' = {fmt(f)} cm, objet à {fmt(do)} cm, image à {fmt(di, 1)} cm), un technicien veut connaître le grandissement pour régler {ctx}. Quelle est sa valeur ?",
            bonne=f"γ = {fmt(gr, 2)} (image renversée, {'agrandie' if abs(gr) > 1 else 'réduite'})", faux=[f"γ = {fmt(-gr, 2)} (image droite, {'agrandie' if abs(gr) > 1 else 'réduite'})", f"γ = {fmt(-1 / gr, 2)} (image renversée)", f"γ = {fmt(-f / do, 2)} (image renversée)", f"γ = 1 (image de même taille)"],
            correction=f"γ = OA'/OA = {fmt(di, 1)}/(−{fmt(do)}) = {fmt(gr, 2)} : le signe négatif indique une image renversée, |γ| {'> 1' if abs(gr) > 1 else '< 1'} une image {'agrandie' if abs(gr) > 1 else 'réduite'}.",
            erreurs=["signe oublié (image droite)", "rapport inversé", "f/do au lieu de di/do", "taille supposée conservée"], figure=fig, legende=leg, rnd=rnd)
    ecran = rnd.choice([round(di) - 2, round(di) + 2, round(di), round(di) + 5])
    ajouter(id_=f"FIG2-PH-len-{k}-3", discipline="Physique", sous=None, epreuve="M.07", chap=chap, difficulte="difficile", type_item="decision", competence="décider",
            savoir="Mise au point : position de l'écran par rapport à l'image", famille="décision professionnelle", titre="Où placer l'écran ?",
            tige=f"L'opérateur de {ctx} (lentille ci-contre, f' = {fmt(f)} cm, objet à {fmt(do)} cm) a fixé l'écran à {fmt(ecran)} cm de la lentille et constate une image floue ou nette. Que doit-il faire, et pourquoi ?",
            bonne=(f"Laisser l'écran, car l'image se forme à OA' = {fmt(di, 1)} cm, à moins d'un demi-centimètre de l'écran" if abs(ecran - di) < 0.5 else
                   f"{'Rapprocher' if ecran > di else 'Éloigner'} l'écran {'de' if abs(ecran - di) >= 1 else 'd'}{'' if abs(ecran - di) >= 1 else 'environ '} {fmt(abs(ecran - di), 1)} cm, car l'image nette se forme à OA' = {fmt(di, 1)} cm"),
            faux=[f"Placer l'écran à {fmt(f)} cm, car l'image d'une lentille convergente est toujours au foyer", f"Placer l'écran à {fmt(do)} cm, car l'image est symétrique de l'objet",
                  f"{'Éloigner' if ecran > di else 'Rapprocher'} l'écran, car l'image se forme à {fmt(do + f, 1)} cm", f"Changer la lentille, car un objet placé à {fmt(do)} cm ne donne pas d'image réelle"],
            correction=f"1/OA' = 1/{fmt(f)} − 1/{fmt(do)} ⇒ OA' = {fmt(di, 1)} cm. L'écran à {fmt(ecran)} cm est {'au bon endroit' if abs(ecran - di) < 0.5 else ('trop loin' if ecran > di else 'trop près') + f' de {fmt(abs(ecran - di), 1)} cm'}. L'objet étant au-delà du foyer, l'image est réelle.",
            erreurs=["image supposée au foyer", "image supposée symétrique", "somme des distances", "image réelle niée"], figure=fig, legende=leg, rnd=rnd)


# ======================================================================================================================
# CHIMIE
# ======================================================================================================================

def c_dosage(rnd: random.Random, k: int):
    Va = rnd.choice([10, 20, 25, 50]); Cb = rnd.choice([0.05, 0.1, 0.2, 0.5]); Ve = rnd.choice([8, 10, 12, 15, 16, 20])
    Ca = Cb * Ve / Va
    def ph(v):
        na, nb = Ca * Va, Cb * v; vt = Va + v
        if nb < na - 1e-9: return -math.log10((na - nb) / vt)
        if nb > na + 1e-9: return 14 + math.log10((nb - na) / vt)
        return 7
    p = Plot(0, 2 * Ve, 0, 14, 460, 320, xstep=Ve / 4 if Ve % 4 == 0 else Ve / 5, ystep=2, xlabel="V (mL)", ylabel="pH", xfmt=lambda v: fmt(v))
    p.curve(ph, 0, 2 * Ve, n=800); p.dashes_to_axes(Ve, 7)
    fig, leg = p.render(), "Courbe de dosage pH = f(V), V volume de soude versé"
    chap = chapitre("Chimie", "titrages")
    ctx = rnd.choice(["une savonnerie contrôle un détartrant", "un laboratoire d'eau contrôle un rejet acide", "une brasserie contrôle un acide de nettoyage", "un centre de santé contrôle une solution acide"])
    ajouter(id_=f"FIG2-CH-dos-{k}-1", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="interpréter",
            savoir="Dosage acide fort – base forte : C_aV_a = C_bV_E", famille="document technique", titre="Concentration d'un acide dosé",
            tige=f"{ctx[0].upper() + ctx[1:]} : {Va} mL d'acide chlorhydrique sont dosés par de la soude à {fmt(Cb)} mol/L ; la courbe pH = f(V) est ci-contre. Quelle est la concentration de l'acide ?",
            bonne=f"{fmt(Ca, 3)} mol/L", faux=[f"{fmt(Cb, 3)} mol/L", f"{fmt(Cb * Va / Ve, 3)} mol/L", f"{fmt(Ca / 2, 3)} mol/L", f"{fmt(Cb * Ve, 3)} mol/L"],
            correction=f"Le saut de pH (équivalence, pH = 7) est à V_E = {Ve} mL. C_a = C_b·V_E/V_a = {fmt(Cb)} × {Ve}/{Va} = {fmt(Ca, 3)} mol/L.",
            erreurs=["concentration de la soude recopiée", "rapport des volumes inversé", "division par 2 injustifiée", "volume non rapporté à V_a"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-CH-dos-{k}-2", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="facile", type_item="classique", competence="interpréter",
            savoir="Lecture du volume équivalent sur une courbe de dosage", famille="document technique", titre="Volume à l'équivalence",
            tige=f"Sur la courbe de dosage ci-contre ({Va} mL d'acide fort par une base forte à {fmt(Cb)} mol/L), un stagiaire doit repérer le volume versé à l'équivalence. Quelle valeur doit-il relever ?",
            bonne=f"{Ve} mL", faux=[f"{Ve // 2 if Ve // 2 != Ve else Ve + 2} mL", f"{2 * Ve} mL", f"{Va} mL" if Va != Ve else f"{Ve + 4} mL", f"7 mL" if Ve != 7 else "14 mL"],
            correction=f"L'équivalence correspond au saut brutal de pH, ici à V_E = {Ve} mL (pH = 7 pour acide fort/base forte).",
            erreurs=["demi-équivalence", "fin de la courbe", "volume d'acide confondu", "pH confondu avec un volume"], figure=fig, legende=leg, rnd=rnd)
    norme = rnd.choice([round(Ca * 0.8, 3), round(Ca * 1.2, 3), round(Ca, 3), round(Ca * 1.5, 3)])
    ajouter(id_=f"FIG2-CH-dos-{k}-3", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Conformité d'une solution à une concentration annoncée", famille="décision professionnelle", titre="Lot conforme ou non ?",
            tige=f"L'étiquette du lot annonce {fmt(norme, 3)} mol/L avec une tolérance de 5 %. {ctx[0].upper() + ctx[1:]} en dosant {Va} mL par de la soude à {fmt(Cb)} mol/L (courbe ci-contre). Que doit conclure le contrôleur, et pourquoi ?",
            bonne=(f"Lot conforme, car C_a = {fmt(Cb)}×{Ve}/{Va} = {fmt(Ca, 3)} mol/L, dans la tolérance autour de {fmt(norme, 3)}" if abs(Ca - norme) <= 0.05 * norme + 1e-9 else f"Lot non conforme, car C_a = {fmt(Cb)}×{Ve}/{Va} = {fmt(Ca, 3)} mol/L, hors de la tolérance autour de {fmt(norme, 3)}"),
            faux=[f"Lot conforme, car le pH à l'équivalence vaut 7 comme attendu", f"Lot {'non conforme' if abs(Cb - norme) > 0.05 * norme else 'conforme'}, car la concentration lue est celle de la soude, {fmt(Cb)} mol/L",
                  f"Lot {'conforme' if abs(Cb * Va / Ve - norme) <= 0.05 * norme else 'non conforme'}, car C_a = {fmt(Cb)}×{Va}/{Ve} = {fmt(Cb * Va / Ve, 3)} mol/L", f"Impossible de conclure sans connaître la masse molaire de l'acide"],
            correction=f"C_a = {fmt(Ca, 3)} mol/L ; écart à {fmt(norme, 3)} : {fmt(100 * abs(Ca - norme) / norme, 1)} %, {'dans' if abs(Ca - norme) <= 0.05 * norme + 1e-9 else 'hors'} tolérance de 5 %. Le pH = 7 à l'équivalence ne renseigne pas sur la concentration.",
            erreurs=["pH d'équivalence pris pour preuve", "concentration de la soude recopiée", "rapport des volumes inversé", "donnée inutile réclamée"], figure=fig, legende=leg, rnd=rnd)


def c_radio(rnd: random.Random, k: int):
    T = rnd.choice([2, 5, 8, 10, 15, 30]); unit = rnd.choice(["jours", "heures", "ans"])
    p = Plot(0, 4 * T, 0, 100, 460, 300, xstep=T / 2 if T >= 8 else T, ystep=20, xlabel=f"t ({unit})", ylabel="activité (%)", xfmt=lambda v: fmt(v))
    p.curve(lambda t: 100 * 0.5 ** (t / T)); p.dashes_to_axes(T, 50); p.dashes_to_axes(2 * T, 25)
    fig, leg = p.render(), "Activité relative d'une source radioactive au cours du temps"
    chap = chapitre("Chimie", "noyau", "radioactivité")
    ctx = rnd.choice(["un service de médecine nucléaire", "un laboratoire de datation", "un entrepôt de sources industrielles", "une mine d'uranium"])
    ajouter(id_=f"FIG2-CH-rad-{k}-1", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="facile", type_item="classique", competence="interpréter",
            savoir="Période radioactive lue sur une courbe de décroissance", famille="document technique", titre="Période d'une source",
            tige=f"Dans {ctx}, la courbe ci-contre donne l'activité d'une source en pourcentage de sa valeur initiale, en fonction du temps. Quelle est la période (demi-vie) de ce radio-isotope ?",
            bonne=f"{fmt(T)} {unit}", faux=[f"{fmt(2 * T)} {unit}", f"{fmt(T / 2)} {unit}", f"{fmt(4 * T)} {unit}", f"50 {unit}" if T != 50 else f"{fmt(3 * T)} {unit}"],
            correction=f"L'activité est tombée à 50 % au bout de {fmt(T)} {unit} : c'est la période T. À 2T ({fmt(2 * T)} {unit}) il reste 25 %.",
            erreurs=["temps pour tomber à 25 %", "demi-période", "fin de la courbe", "pourcentage confondu avec le temps"], figure=fig, legende=leg, rnd=rnd)
    n = rnd.choice([3, 4, 5])
    ajouter(id_=f"FIG2-CH-rad-{k}-2", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Fraction restante après n périodes : (1/2)ⁿ", famille="document technique", titre="Activité après plusieurs périodes",
            tige=f"La source dont la courbe de décroissance est ci-contre (période {fmt(T)} {unit}) est entreposée dans {ctx} pendant {fmt(n * T)} {unit} sans être utilisée. Le responsable doit inscrire sur l'étiquette le pourcentage de l'activité initiale qui reste alors. Quelle valeur doit-il inscrire ?",
            bonne=f"{fmt(100 / 2 ** n, 2)} %", faux=[f"{fmt(100 / (2 * n), 2)} %", f"{fmt(100 - 50 * n, 2) if 100 - 50 * n > 0 else '0'} %", f"{fmt(100 / n, 2)} %", f"{fmt(100 / 2 ** (n - 1), 2)} %"],
            correction=f"{fmt(n * T)} {unit} = {n} périodes ; il reste (1/2)^{n} = 1/{2 ** n} de l'activité, soit {fmt(100 / 2 ** n, 2)} %.",
            erreurs=["division par 2n au lieu de 2ⁿ", "décroissance supposée linéaire", "division par n", "une période de moins"], figure=fig, legende=leg, rnd=rnd)
    seuil = rnd.choice([10, 5, 1]); n_req = math.ceil(math.log2(100 / seuil)); t_req = n_req * T
    prop = rnd.choice([t_req, t_req - T, t_req + T])
    ajouter(id_=f"FIG2-CH-rad-{k}-3", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="difficile", type_item="decision", competence="décider",
            savoir="Durée d'entreposage avant de passer sous un seuil d'activité", famille="décision professionnelle", titre="Peut-on évacuer la source ?",
            tige=f"Le règlement de {ctx} autorise l'évacuation d'une source quand son activité est passée sous {seuil} % de la valeur initiale. La courbe ci-contre a pour période {fmt(T)} {unit} ; la source est entreposée depuis {fmt(prop)} {unit}. Que doit faire le responsable, et pourquoi ?",
            bonne=(f"Évacuer, car après {prop // T} périodes il reste {fmt(100 / 2 ** (prop // T), 2)} %, sous le seuil de {seuil} %" if 100 / 2 ** (prop // T) < seuil else f"Attendre encore, car après {prop // T} périodes il reste {fmt(100 / 2 ** (prop // T), 2)} %, au-dessus du seuil de {seuil} %"),
            faux=[(f"Attendre encore, car {prop // T} périodes ne suffisent jamais" if 100 / 2 ** (prop // T) < seuil else f"Évacuer, car {prop // T} périodes suffisent toujours"),
                  f"{'Évacuer' if 100 - 50 * (prop / T) < seuil else 'Attendre encore'}, car l'activité baisse de 50 % par période, soit {fmt(max(0, 100 - 50 * prop / T), 0)} % restants",
                  f"Évacuer, car {fmt(prop)} {unit} dépassent la période {fmt(T)} {unit}", f"Attendre encore, car l'activité ne devient jamais nulle"],
            correction=f"Après {prop // T} périodes : (1/2)^{prop // T} = {fmt(100 / 2 ** (prop // T), 2)} %, {'inférieur' if 100 / 2 ** (prop // T) < seuil else 'supérieur'} à {seuil} %. Il faut {n_req} périodes ({fmt(t_req)} {unit}) pour passer sous {seuil} %. La décroissance n'est pas linéaire.",
            erreurs=["raisonnement sans calcul", "décroissance supposée linéaire", "une période prise pour suffisante", "seuil ignoré"], figure=fig, legende=leg, rnd=rnd)


def c_chromato(rnd: random.Random, k: int):
    H = rnd.choice([6, 8, 10]); h1 = rnd.choice([1.5, 2, 2.5, 3]); h2 = rnd.choice([4, 4.5, 5, 6]); h2 = min(h2, H - 1)
    fig = chromatogramme([("E", [h1]), ("R", [h2]), ("M", [h1, h2])], float(H)); leg = "Chromatogramme des dépôts E, R et M (règle en cm)"
    chap = chapitre("Chimie", "chromatographie", "séparation")
    ctx = rnd.choice(["un colorant de marché", "une encre de bulletin de vote", "un sirop de pharmacie", "un pigment de peinture"])
    rf1 = h1 / H; rf2 = h2 / H
    ajouter(id_=f"FIG2-CH-chr-{k}-1", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Rapport frontal R_f = h/H", famille="document à lire", titre="Rapport frontal d'un constituant",
            tige=f"Un inspecteur analyse {ctx} (dépôt M) à côté de deux références E et R ; le chromatogramme ci-contre porte une règle en cm, le front du solvant est à {H} cm. Quel est le rapport frontal du constituant commun à E et M ?",
            bonne=fmt(rf1, 3), faux=[fmt(rf2, 3), fmt(h1, 3), fmt(H / h1, 3), fmt(h1 / h2, 3)],
            correction=f"La tache commune à E et M est à h = {fmt(h1)} cm ; R_f = h/H = {fmt(h1)}/{H} = {fmt(rf1, 3)}.",
            erreurs=["R_f de la tache de R", "hauteur sans division", "rapport inversé", "rapport entre taches"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-CH-chr-{k}-2", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="facile", type_item="classique", competence="interpréter",
            savoir="Lecture d'un chromatogramme : corps pur ou mélange", famille="document à lire", titre="Nature du dépôt M",
            tige=f"Sur le chromatogramme ci-contre, le dépôt M ({ctx}) est comparé aux références E et R, déposées pures dans les mêmes conditions. L'inspecteur doit écrire une conclusion dans son rapport. Que peut-on conclure sur la nature de M ?",
            bonne="M est un mélange contenant E et R", faux=["M est un corps pur identique à E", "M est un corps pur identique à R", "M ne contient ni E ni R", "M contient E mais pas R"],
            correction=f"M donne deux taches, aux mêmes hauteurs ({fmt(h1)} et {fmt(h2)} cm) que E et R : M est un mélange de ces deux constituants.",
            erreurs=["une seule tache retenue", "seule la tache haute retenue", "lecture inversée", "seconde tache ignorée"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-CH-chr-{k}-3", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Comparaison de rapports frontaux pour identifier un constituant", famille="décision professionnelle", titre="Retirer le produit de la vente ?",
            tige=f"Le constituant R est interdit dans les produits alimentaires ; son R_f de référence vaut {fmt(rf2, 2)}. L'inspecteur a obtenu le chromatogramme ci-contre pour {ctx} (dépôt M, front à {H} cm). Que doit-il décider, et pourquoi ?",
            bonne=f"Retirer le produit, car M contient une tache à {fmt(h2)} cm, soit R_f = {fmt(rf2, 2)}, celui de R",
            faux=[f"Garder le produit, car la tache de M à {fmt(h1)} cm a un R_f de {fmt(rf1, 2)}, différent de {fmt(rf2, 2)}", f"Garder le produit, car M a deux taches alors que R n'en a qu'une",
                  f"Retirer le produit, car toute tache au-dessus de {fmt(h1)} cm est suspecte", f"Impossible de conclure, car un R_f dépend seulement de la couleur de la tache"],
            correction=f"M présente une tache à {fmt(h2)} cm, soit R_f = {fmt(h2)}/{H} = {fmt(rf2, 2)}, identique à celui de R dans les mêmes conditions : R est présent, le produit doit être retiré. L'autre tache (E) n'y change rien.",
            erreurs=["seule la première tache examinée", "nombre de taches mal interprété", "critère arbitraire", "notion de R_f mal comprise"], figure=fig, legende=leg, rnd=rnd)


def c_dilution(rnd: random.Random, k: int):
    C0 = rnd.choice([0.5, 1, 2, 5]); V0 = rnd.choice([5, 10, 20, 25, 50]); V1 = V0 * rnd.choice([4, 5, 10, 20])
    C1 = C0 * V0 / V1
    fig = table(["Solution", "Concentration", "Volume prélevé", "Volume final"], [["Mère S₀", f"{fmt(C0)} mol/L", "—", "—"], ["Fille S₁", "?", f"{V0} mL", f"{V1} mL"]], col_w=[100, 120, 120, 110], first_col_bold=True)
    leg = "Fiche de préparation d'une solution diluée"
    chap = chapitre("Chimie", "solutions", "concentration")
    ctx = rnd.choice(["un dispensaire prépare une solution de glucose", "une brasserie prépare une solution de nettoyage", "un laboratoire scolaire prépare une solution d'acide", "une station de traitement prépare une solution de chlore"])
    ajouter(id_=f"FIG2-CH-dil-{k}-1", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Dilution : C₀V₀ = C₁V₁", famille="document à lire", titre="Concentration d'une solution fille",
            tige=f"La fiche ci-contre indique comment {ctx} : {V0} mL de la solution mère à {fmt(C0)} mol/L sont complétés à {V1} mL avec de l'eau distillée. Quelle est la concentration de la solution fille ?",
            bonne=f"{fmt(C1, 3)} mol/L", faux=[f"{fmt(C0 * V1 / V0, 3)} mol/L", f"{fmt(C0 / 2, 3)} mol/L", f"{fmt(C0, 3)} mol/L", f"{fmt(C0 * V0 / (V1 - V0), 3)} mol/L"],
            correction=f"C₁ = C₀V₀/V₁ = {fmt(C0)} × {V0}/{V1} = {fmt(C1, 3)} mol/L (facteur de dilution {V1 // V0}).",
            erreurs=["rapport inversé", "division par 2 arbitraire", "dilution ignorée", "volume d'eau ajouté pris pour volume final"], figure=fig, legende=leg, rnd=rnd)
    Cv = rnd.choice([C1 / 2, C1 * 2, C1 / 5]); Vv = C0 * 0 + 100
    Vp = Cv * Vv / C0
    ajouter(id_=f"FIG2-CH-dil-{k}-2", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Volume à prélever pour une dilution donnée", famille="document à lire", titre="Volume de solution mère à prélever",
            tige=f"Avec la même solution mère S₀ à {fmt(C0)} mol/L (fiche ci-contre), on veut préparer {Vv} mL d'une solution à {fmt(Cv, 3)} mol/L. Quel volume de S₀ faut-il prélever ?",
            bonne=f"{fmt(Vp, 2)} mL", faux=[f"{fmt(Vv * C0 / Cv, 2)} mL", f"{fmt(Vp * 10, 2)} mL", f"{fmt(Vv - Vp, 2)} mL", f"{fmt(Cv * C0, 2)} mL"],
            correction=f"V₀ = C₁V₁/C₀ = {fmt(Cv, 3)} × {Vv}/{fmt(C0)} = {fmt(Vp, 2)} mL, à compléter à {Vv} mL.",
            erreurs=["rapport inversé", "erreur d'un facteur 10", "volume d'eau donné pour le prélèvement", "produit des concentrations"], figure=fig, legende=leg, rnd=rnd)
    cible = rnd.choice([C1, C1 * 2, C1 / 2])
    ajouter(id_=f"FIG2-CH-dil-{k}-3", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Vérification d'une préparation par la relation de dilution", famille="décision professionnelle", titre="La préparation est-elle correcte ?",
            tige=f"Le protocole exige une solution à {fmt(cible, 3)} mol/L. Un préparateur a suivi la fiche ci-contre ({V0} mL de S₀ à {fmt(C0)} mol/L complétés à {V1} mL). Son chef doit-il valider la préparation, et pourquoi ?",
            bonne=(f"Oui, car C₁ = {fmt(C0)}×{V0}/{V1} = {fmt(C1, 3)} mol/L, la concentration exigée" if abs(C1 - cible) < 1e-9 else f"Non, car C₁ = {fmt(C0)}×{V0}/{V1} = {fmt(C1, 3)} mol/L, {'le double' if C1 > cible else 'la moitié'} de la concentration exigée"),
            faux=[(f"Non, car C₁ = {fmt(C0)}×{V1}/{V0} = {fmt(C0 * V1 / V0, 1)} mol/L" if abs(C1 - cible) < 1e-9 else f"Oui, car {V0} mL de S₀ donnent toujours la bonne concentration"),
                  f"Oui, car la quantité de matière, {fmt(C0 * V0 / 1000, 4)} mol, est conservée", f"Non, car il fallait ajouter exactement {V1 - V0} mL d'eau, pas compléter à {V1} mL", f"Impossible de conclure sans la masse molaire du soluté"],
            correction=f"C₁ = C₀V₀/V₁ = {fmt(C1, 3)} mol/L à comparer à {fmt(cible, 3)} mol/L : {'conforme' if abs(C1 - cible) < 1e-9 else 'non conforme'}. La conservation de la quantité de matière est vraie mais ne suffit pas à conclure.",
            erreurs=["rapport inversé ou conclusion sans calcul", "conservation invoquée sans comparer", "volume d'eau ajouté confondu avec volume final", "donnée inutile réclamée"], figure=fig, legende=leg, rnd=rnd)


def c_atome(rnd: random.Random, k: int):
    Z = rnd.choice([6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 20])
    noms = {6: "carbone", 7: "azote", 8: "oxygène", 9: "fluor", 11: "sodium", 12: "magnésium", 13: "aluminium", 14: "silicium", 15: "phosphore", 16: "soufre", 17: "chlore", 19: "potassium", 20: "calcium"}
    ordre = [("1s", 1), ("2s", 1), ("2p", 3), ("3s", 1), ("3p", 3), ("4s", 1)]
    cfg, reste, val = [], Z, 0
    for sc, nc in ordre:
        if reste <= 0: break
        n = min(reste, 2 * nc); reste -= n
        cases = [0] * nc
        for i in range(n):  # Hund
            cases[i % nc] += 1
        cfg.append((sc, cases))
    couche = max(int(sc[0]) for sc, _ in cfg); val = sum(sum(c) for sc, c in cfg if int(sc[0]) == couche)
    fig = cases_quantiques(cfg); leg = "Diagramme de cases quantiques de l'atome à l'état fondamental"
    chap = chapitre("Chimie", "atome", "structure électronique")
    ajouter(id_=f"FIG2-CH-ato-{k}-1", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="classique", competence="identifier",
            savoir="Numéro atomique à partir de la configuration électronique", famille="document graphique", titre="Identifier un élément par ses cases",
            tige=f"Une fiche de laboratoire présente le diagramme de cases quantiques ci-contre d'un atome neutre à l'état fondamental, rempli selon la règle de Hund. En comptant les électrons, quel est le numéro atomique Z de cet élément ?",
            bonne=f"{Z}", faux=[f"{Z - val}", f"{Z + 1}", f"{val}", f"{Z - 1}" if Z - 1 != Z - val else f"{Z + 2}"],
            correction=f"Électrons : {' '.join(f'{sc}{sum(c)}' for sc, c in cfg)} = {Z}. Atome neutre : Z = {Z} ({noms[Z]}).",
            erreurs=["couche de valence oubliée", "un électron de trop", "seule la couche de valence comptée", "un électron oublié"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-CH-ato-{k}-2", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="facile", type_item="classique", competence="interpréter",
            savoir="Électrons de valence et couche externe", famille="document graphique", titre="Électrons de valence",
            tige=f"La fiche de laboratoire ci-contre donne le diagramme de cases quantiques d'un atome neutre à l'état fondamental. Pour prévoir ses liaisons chimiques, un préparateur doit compter ses électrons de valence. Combien d'électrons l'atome possède-t-il sur sa couche externe ?",
            bonne=f"{val}", faux=[f"{Z}", f"{8 - val if 8 - val not in (val, Z) else val + 2}", f"{sum(1 for sc, c in cfg if int(sc[0]) == couche for x in c if x == 1)}" if sum(1 for sc, c in cfg if int(sc[0]) == couche for x in c if x == 1) not in (val, Z, 8 - val) else f"{val + 1}", f"{couche}"],
            correction=f"Couche externe n = {couche} : {' '.join(f'{sc}{sum(c)}' for sc, c in cfg if int(sc[0]) == couche)} = {val} électrons de valence.",
            erreurs=["tous les électrons comptés", "électrons manquants pour l'octet", "électrons célibataires seulement", "numéro de couche confondu"], figure=fig, legende=leg, rnd=rnd)
    ion = -(8 - val) if val >= 5 else val
    ajouter(id_=f"FIG2-CH-ato-{k}-3", discipline="Chimie", sous=None, epreuve="M.07", chap=chap, difficulte="moyen", type_item="decision", competence="raisonner",
            savoir="Ion le plus stable d'après la règle de l'octet", famille="document graphique", titre="Quel ion forme cet élément ?",
            tige=f"Un chimiste doit prévoir l'ion que forme l'élément dont le diagramme de cases est ci-contre, pour écrire la formule d'un sel. En appliquant la règle de l'octet à la couche externe, quel ion doit-il attendre, et pourquoi ?",
            bonne=(f"Un cation {noms[Z].capitalize()}{'' if ion == 1 else ion}⁺, car il perd ses {val} électron(s) de valence pour retrouver l'octet de la couche précédente" if ion > 0 else f"Un anion {noms[Z].capitalize()}{'' if ion == -1 else -ion}⁻, car il gagne {-ion} électron(s) pour compléter l'octet"),
            faux=[(f"Un anion {noms[Z].capitalize()}{val}⁻, car il gagne autant d'électrons qu'il en a sur la couche externe" if ion > 0 else f"Un cation {noms[Z].capitalize()}{-ion}⁺, car il perd {-ion} électrons"),
                  f"Aucun ion, car la couche externe est déjà saturée", f"Un cation {noms[Z].capitalize()}{Z}⁺, car il perd tous ses électrons", f"Un anion, car tout atome cherche à gagner des électrons"],
            correction=f"Couche externe à {val} électron(s) : {'perte' if ion > 0 else 'gain'} de {abs(ion)} électron(s) pour un octet, d'où l'ion {noms[Z]}{abs(ion) if abs(ion) != 1 else ''}{'⁺' if ion > 0 else '⁻'}.",
            erreurs=["sens du transfert inversé", "saturation supposée", "tous les électrons perdus", "gain supposé systématique"], figure=fig, legende=leg, rnd=rnd)


# ======================================================================================================================
# SVT
# ======================================================================================================================

def s_logistique(rnd: random.Random, k: int):
    K = rnd.choice([400, 600, 800, 1000, 1500]); N0 = rnd.choice([20, 50, 100]); r = rnd.choice([0.3, 0.4, 0.5, 0.6])
    esp = rnd.choice(["tilapias dans un bassin", "chèvres dans un enclos", "poulets dans un poulailler", "abeilles dans une ruche (en centaines)", "tilapias dans un étang"])
    p = Plot(0, 24, 0, K * 1.2, 480, 300, xstep=4, ystep=K / 4 if K % 4 == 0 else K / 5, xlabel="semaines", ylabel="effectif", yfmt=lambda v: fmt(round(v)))
    p.curve(lambda t: K / (1 + (K / N0 - 1) * math.exp(-r * t))); p.segment(0, K, 24, K, ROUGE, 1.4, dash="6 4")
    fig, leg = p.render(), f"Effectif de {esp} au cours du temps"
    chap = chapitre("SVT", "concepts écologiques", "écosystèmes"); sd = "Écologie"
    ajouter(id_=f"FIG2-SV-log-{k}-1", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="moyen", type_item="classique", competence="interpréter",
            savoir="Croissance logistique et capacité limite du milieu", famille="donnée brute", titre="Capacité limite d'un milieu",
            tige=f"Le registre d'un éleveur donne l'effectif de {esp} après l'introduction de {N0} individus, sans prélèvement ni apport (courbe ci-contre, avec une droite rouge en pointillés). Que représente la valeur {K} marquée par cette droite ?",
            bonne="La capacité limite du milieu : effectif maximal que les ressources peuvent entretenir", faux=["L'effectif initial introduit", "Le taux de croissance hebdomadaire", "L'effectif au bout de quatre semaines", "La quantité de nourriture distribuée"],
            correction=f"La courbe en S se stabilise sous l'asymptote {K} : c'est la capacité limite (capacité de charge) imposée par l'espace, la nourriture et l'oxygène disponibles.",
            erreurs=["effectif initial lu à t = 0", "taux confondu avec un effectif", "lecture à un instant donné", "information absente du graphique"], figure=fig, legende=leg, rnd=rnd)
    t_half = math.log(K / N0 - 1) / r
    ajouter(id_=f"FIG2-SV-log-{k}-2", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="facile", type_item="classique", competence="interpréter",
            savoir="Phases d'une croissance logistique : exponentielle, ralentissement, plateau", famille="donnée brute", titre="Phase de croissance la plus rapide",
            tige=f"Sur la courbe ci-contre ({esp}, capacité limite {K}), l'éleveur veut savoir à quel moment la population a gagné le plus d'individus par semaine. Quelle lecture est correcte ?",
            bonne=f"Vers la {round(t_half)}ᵉ semaine, quand l'effectif vaut environ la moitié de {K}", faux=["Au tout début, quand l'effectif est le plus faible", f"Vers la 24ᵉ semaine, quand l'effectif est maximal", "Jamais : la croissance est constante", "Au moment où la courbe atteint la droite rouge"],
            correction=f"La pente de la courbe est maximale au point d'inflexion, vers la {round(t_half)}ᵉ semaine, pour un effectif voisin de K/2 = {K // 2} ; ensuite la croissance ralentit jusqu'au plateau.",
            erreurs=["début confondu avec croissance rapide", "effectif maximal confondu avec croissance maximale", "croissance supposée linéaire", "plateau confondu avec croissance"], figure=fig, legende=leg, rnd=rnd)
    cible = rnd.choice([round(K * 0.8), round(K * 0.6), round(K * 1.2)])
    t_c = math.log((K / cible - 1) / (K / N0 - 1)) / (-r) if cible < K else None
    ajouter(id_=f"FIG2-SV-log-{k}-3", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Capacité limite et décision d'élevage", famille="décision professionnelle", titre="Objectif atteignable ?",
            tige=f"Un acheteur commande {cible} {esp.split(' ')[0]} à prélever d'un seul coup dans ce bassin, dont la dynamique est celle de la courbe ci-contre (capacité limite {K}). Que doit répondre l'éleveur, et pourquoi ?",
            bonne=(f"Accepter, car l'effectif atteint {cible} vers la {round(t_c)}ᵉ semaine, sous la capacité limite {K}" if cible < K else f"Refuser, car {cible} dépasse la capacité limite {K} : l'effectif ne l'atteindra jamais sans agrandir le bassin"),
            faux=[(f"Refuser, car l'effectif initial {N0} est trop faible pour atteindre {cible}" if cible < K else f"Accepter, car la croissance continue indéfiniment avec le temps"),
                  f"Accepter, car {cible} est inférieur à {K} × 24 semaines", f"Refuser, car la population diminue après la {round(t_half)}ᵉ semaine", f"Accepter à condition d'attendre exactement {round(K / cible)} semaines"],
            correction=f"La capacité limite {K} borne l'effectif. {('Un objectif de ' + str(cible) + ' est atteignable, vers la ' + str(round(t_c)) + 'ᵉ semaine') if cible < K else ('Un objectif de ' + str(cible) + ' dépasse K et n est jamais atteint')}.",
            erreurs=["effectif initial pris pour limite ou croissance supposée illimitée", "calcul sans sens", "ralentissement confondu avec diminution", "durée inventée"], figure=fig, legende=leg, rnd=rnd)


def s_punnett(rnd: random.Random, k: int):
    mono = rnd.random() < 0.5
    trait = rnd.choice([("A", "pelage noir", "pelage blanc", "lapins"), ("R", "grains rouges", "grains blancs", "plants de maïs"), ("C", "cornes présentes", "sans cornes", "chèvres"), ("L", "feuilles lisses", "feuilles ridées", "plants de haricot")])
    g = trait[0]
    if mono:
        fig = punnett([g, g.lower()], [g, g.lower()], w_cell=74); leg = f"Échiquier de croisement {g}{g.lower()} × {g}{g.lower()}"
        chap = chapitre("SVT", "génétique", "monohybridisme"); sd = "Biologie"
        ajouter(id_=f"FIG2-SV-pun-{k}-1", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
                savoir="Monohybridisme : proportions 3:1 en F2", famille="scène de travail", titre="Proportion de récessifs en F2",
                tige=f"Un éleveur croise des {trait[3]} hétérozygotes {g}{g.lower()} ({g} : {trait[1]}, dominant ; {g.lower()} : {trait[2]}). L'échiquier ci-contre donne la descendance. Quelle proportion d'individus à {trait[2]} attend-il ?",
                bonne="1/4", faux=["1/2", "3/4", "1/16", "2/3"],
                correction=f"Seul le génotype {g.lower()}{g.lower()} (une case sur quatre) donne le phénotype récessif {trait[2]} : 1/4. Les trois autres cases ({g}{g}, {g}{g.lower()}, {g}{g.lower()}) donnent {trait[1]}.",
                erreurs=["hétérozygotes comptés", "phénotype dominant", "proportion du dihybridisme", "fraction mal lue"], figure=fig, legende=leg, rnd=rnd)
        ajouter(id_=f"FIG2-SV-pun-{k}-2", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="moyen", type_item="classique", competence="raisonner",
                savoir="Génotypes et phénotypes dans un croisement entre hétérozygotes", famille="scène de travail", titre="Part des hétérozygotes parmi les dominants",
                tige=f"L'échiquier ci-contre décrit le croisement {g}{g.lower()} × {g}{g.lower()} chez des {trait[3]}. L'éleveur veut garder, parmi les descendants à {trait[1]}, ceux qui ne transmettront pas l'allèle {g.lower()}. Parmi ces descendants à {trait[1]}, quelle proportion est hétérozygote et transmettra donc l'allèle {g.lower()} ?",
                bonne="2/3", faux=["1/2", "1/4", "3/4", "1/3"],
                correction=f"Trois cases donnent {trait[1]} : {g}{g}, {g}{g.lower()}, {g}{g.lower()} ; deux sur trois sont hétérozygotes : 2/3.",
                erreurs=["proportion rapportée à toute la descendance", "homozygotes récessifs", "dominants rapportés au total", "homozygotes dominants parmi les dominants"], figure=fig, legende=leg, rnd=rnd)
        n = rnd.choice([40, 60, 80, 100]); obs = round(n * rnd.choice([0.05, 0.25, 0.5]))
        ajouter(id_=f"FIG2-SV-pun-{k}-3", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
                savoir="Comparaison d'un résultat observé aux proportions attendues", famille="décision professionnelle", titre="Les parents étaient-ils hétérozygotes ?",
                tige=f"Sur {n} {trait[3]} issus d'un croisement, un éleveur compte {obs} individus à {trait[2]} (récessif). Il hésite entre deux hypothèses : parents hétérozygotes (échiquier ci-contre) ou croisement {g}{g} × {g}{g.lower()}. Que doit-il conclure, et pourquoi ?",
                bonne=(f"Parents hétérozygotes, car {obs}/{n} ≈ {fmt(100 * obs / n, 0)} % est proche du 1/4 attendu" if abs(obs / n - 0.25) < 0.1 else (f"Croisement {g}{g} × {g}{g.lower()} probable, car {obs}/{n} ≈ {fmt(100 * obs / n, 0)} % est loin du 1/4 attendu et proche de 0 récessif" if obs / n < 0.15 else f"Un croisement {g}{g.lower()} × {g.lower()}{g.lower()}, car {obs}/{n} ≈ {fmt(100 * obs / n, 0)} % est proche de 1/2")),
                faux=[f"Parents hétérozygotes, car tout croisement donne 1/4 de récessifs", f"Croisement {g}{g} × {g}{g.lower()}, car il ne donne jamais de {trait[2]} : la lecture de {obs} est une erreur",
                      f"Impossible de conclure, car {n} individus ne suffisent pas", f"Parents hétérozygotes, car {obs} est inférieur à {n}/2"],
                correction=f"Proportion observée {obs}/{n} = {fmt(100 * obs / n, 0)} %. Hétérozygotes × hétérozygotes attendent 25 % ; {g}{g} × {g}{g.lower()} attend 0 % ; {g}{g.lower()} × {g.lower()}{g.lower()} attend 50 %. La valeur observée tranche.",
                erreurs=["proportion supposée universelle", "donnée rejetée sans raison", "effectif suffisant pourtant", "comparaison hors sujet"], figure=fig, legende=leg, rnd=rnd)
    else:
        B = rnd.choice(["B", "T", "V"])
        gam = [g + B, g + B.lower(), g.lower() + B, g.lower() + B.lower()]
        kf = lambda c: (c.lower(), c.islower())
        cel = lambda m, f: "".join(sorted(m[0] + f[0], key=kf)) + "".join(sorted(m[1] + f[1], key=kf))
        fig = punnett(gam, gam, cel, w_cell=66); leg = f"Échiquier de croisement {g}{g.lower()}{B}{B.lower()} × {g}{g.lower()}{B}{B.lower()}"
        chap = chapitre("SVT", "dihybridisme", "génétique"); sd = "Biologie"
        ajouter(id_=f"FIG2-SV-pun-{k}-1", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
                savoir="Dihybridisme : proportions 9:3:3:1", famille="scène de travail", titre="Double récessif en F2",
                tige=f"Une coopérative croise des {trait[3]} doubles hétérozygotes {g}{g.lower()}{B}{B.lower()} (gènes indépendants ; {g} : {trait[1]} dominant ; {B} : second caractère dominant). L'échiquier ci-contre donne la F2. Quelle proportion de doubles récessifs attend-on ?",
                bonne="1/16", faux=["3/16", "9/16", "1/4", "1/8"],
                correction=f"Le génotype {g.lower()}{g.lower()}{B.lower()}{B.lower()} n'occupe qu'une case sur 16 (gamètes {g.lower()}{B.lower()} × {g.lower()}{B.lower()}) : 1/16. Les autres classes : 9/16 double dominant, 3/16 et 3/16 simples récessifs.",
                erreurs=["classe simple récessive", "classe double dominante", "raisonnement monohybride", "fraction fausse"], figure=fig, legende=leg, rnd=rnd)
        ajouter(id_=f"FIG2-SV-pun-{k}-2", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="moyen", type_item="classique", competence="raisonner",
                savoir="Phénotypes recombinés dans un dihybridisme", famille="scène de travail", titre="Phénotype {0} et second caractère récessif".format(trait[1]),
                tige=f"L'échiquier ci-contre décrit le croisement {g}{g.lower()}{B}{B.lower()} × {g}{g.lower()}{B}{B.lower()} chez des {trait[3]}, pour deux gènes indépendants. La coopérative recherche les descendants qui présentent {trait[1]} (dominant) et le second caractère à l'état récessif. Quelle proportion de la descendance attend-elle ?",
                bonne="3/16", faux=["1/16", "9/16", "1/4", "6/16"],
                correction=f"Il faut au moins un {g} et deux {B.lower()} : génotypes {g}{g}{B.lower()}{B.lower()} (1 case) et {g}{g.lower()}{B.lower()}{B.lower()} (2 cases) = 3 cases sur 16.",
                erreurs=["double récessif", "double dominant", "raisonnement monohybride", "cases hétérozygotes mal comptées"], figure=fig, legende=leg, rnd=rnd)
        n = 160
        ajouter(id_=f"FIG2-SV-pun-{k}-3", discipline="SVT", sous=sd, epreuve="M.46", chap=chapitre("SVT", "khi", "probabilités"), difficulte="difficile", type_item="decision", competence="décider",
                savoir="Effectifs attendus 9:3:3:1 et comparaison aux effectifs observés", famille="décision professionnelle", titre="Les gènes sont-ils indépendants ?",
                tige=f"Sur {n} {trait[3]} de F2, le technicien observe {n * 9 // 16 + rnd.choice([-3, 0, 2])} doubles dominants, {n * 3 // 16} et {n * 3 // 16 + rnd.choice([-1, 1])} simples récessifs et {n // 16 + rnd.choice([0, 1])} doubles récessifs ; l'échiquier ci-contre suppose des gènes indépendants. Que doit-il conclure, et pourquoi ?",
                bonne=f"Les gènes semblent indépendants, car les effectifs attendus 90 : 30 : 30 : 10 sont proches des observés",
                faux=[f"Les gènes sont liés, car les quatre classes ne sont pas égales ({n // 4} chacune)", f"Les gènes sont liés, car les doubles récessifs sont trop rares", f"Impossible de conclure sans croiser avec un double récessif", f"Les gènes semblent indépendants, car 9 + 3 + 3 + 1 = 16"],
                correction=f"Attendus sous l'hypothèse d'indépendance : {n}×9/16 = 90, {n}×3/16 = 30, 30, {n}/16 = 10. Les observés en sont très proches : hypothèse d'indépendance retenue (un test du khi-carré le confirmerait).",
                erreurs=["égalité des classes attendue à tort", "rareté normale du double récessif", "test-cross inutile ici", "somme des coefficients sans comparaison"], figure=fig, legende=leg, rnd=rnd)


def s_pedigree(rnd: random.Random, k: int):
    liee = rnd.random() < 0.5
    mal = rnd.choice(["daltonisme", "hémophilie"]) if liee else rnd.choice(["albinisme", "drépanocytose", "mucoviscidose"])
    mal_art = ("l'" if mal[0] in "aeiouhé" else "la ") + mal
    fig = pedigree(
        [[{"id": "I1", "sexe": "M", "atteint": False, "label": "1"}, {"id": "I2", "sexe": "F", "atteint": False, "label": "2"}],
         [{"id": "II1", "sexe": "M", "atteint": True, "label": "1"}, {"id": "II2", "sexe": "F", "atteint": False, "label": "2"}, {"id": "II3", "sexe": "M", "atteint": False, "label": "3"}],
         [{"id": "III1", "sexe": "M" if liee else rnd.choice(["M", "F"]), "atteint": False, "label": "1", "q": True}]],
        [("I1", "I2"), ("II2", "II3")], [(0, ["II1", "II2"]), (1, ["III1"])])
    leg = f"Arbre généalogique : {mal} (individus atteints en noir)"
    chap = chapitre("SVT", "génétique humaine"); sd = "Biologie"
    if liee:
        ajouter(id_=f"FIG2-SV-ped-{k}-1", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="moyen", type_item="classique", competence="raisonner",
                savoir="Hérédité récessive liée à l'X : génotype d'une mère de garçon atteint", famille="document à lire", titre=f"Génotype de la mère ({mal})",
                tige=f"L'arbre ci-contre, dressé par un médecin, concerne le {mal}, anomalie récessive liée au chromosome X. Le garçon II1 est atteint, ses parents I1 et I2 sont sains. Quel est le génotype de la mère I2 ?",
                bonne="Xᴰ Xᵈ (conductrice)", faux=["Xᴰ Xᴰ (non porteuse)", "Xᵈ Xᵈ (atteinte)", "Xᴰ Y", "Impossible à déterminer"],
                correction="II1 est Xᵈ Y ; son X vient de sa mère, qui porte donc Xᵈ ; étant saine, son autre X est Xᴰ : I2 est Xᴰ Xᵈ, conductrice.",
                erreurs=["mère supposée non porteuse", "mère supposée atteinte", "génotype masculin", "raisonnement non mené"], figure=fig, legende=leg, rnd=rnd)
        ajouter(id_=f"FIG2-SV-ped-{k}-2", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="difficile", type_item="classique", competence="calculer",
                savoir="Probabilité d'un garçon atteint via une mère possiblement conductrice", famille="document à lire", titre=f"Risque pour III1 ({mal})",
                tige=f"Toujours pour le {mal} (anomalie récessive liée à l'X, arbre ci-contre), II2 est saine et son mari II3 est sain ; ils attendent un garçon, III1. Quelle est la probabilité que ce fils soit atteint ?",
                bonne="1/4", faux=["1/2", "0", "1", "1/8"],
                correction="II2 a reçu Xᴰ de son père et Xᴰ ou Xᵈ de sa mère conductrice : P(conductrice) = 1/2. Un fils d'une conductrice reçoit Xᵈ avec probabilité 1/2. Total : 1/2 × 1/2 = 1/4.",
                erreurs=["II2 supposée conductrice à coup sûr", "transmission par une mère saine niée", "fils d'une mère atteinte", "sexe déjà connu compté deux fois"], figure=fig, legende=leg, rnd=rnd)
        ajouter(id_=f"FIG2-SV-ped-{k}-3", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
                savoir="Conseil génétique : qui dépister dans une hérédité liée à l'X", famille="décision professionnelle", titre="Qui faut-il tester ?",
                tige=f"Le médecin doit conseiller un test de détection de l'allèle du {mal} (récessif, lié à l'X) à la personne de la génération II dont le statut est incertain et qui pourrait transmettre l'anomalie (arbre ci-contre). Que doit-il décider, et pourquoi ?",
                bonne="Tester II2, car fille d'une conductrice, elle a une chance sur deux d'être conductrice sans le savoir", faux=["Tester II3, car un homme sain peut transmettre l'allèle à ses fils", "Tester II1, car son statut détermine celui de ses sœurs", "Ne tester personne, car l'anomalie saute une génération", "Tester I1, car le père transmet l'X à ses fils"],
                correction="Les hommes sains ne portent pas l'allèle (un seul X, Xᴰ) ; II1 est atteint, son statut est connu. Seule II2, fille d'une mère Xᴰ Xᵈ, est conductrice avec une probabilité 1/2 : c'est elle qu'il faut tester.",
                erreurs=["homme sain supposé porteur", "statut déjà connu", "saut de génération mal compris", "transmission père-fils de l'X impossible"], figure=fig, legende=leg, rnd=rnd)
    else:
        ajouter(id_=f"FIG2-SV-ped-{k}-1", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="moyen", type_item="classique", competence="raisonner",
                savoir="Hérédité autosomale récessive : parents hétérozygotes", famille="document à lire", titre=f"Génotype des parents ({mal})",
                tige=f"L'arbre ci-contre concerne {mal_art} (on note a l'allèle muté), anomalie autosomale récessive. L'enfant II1 est atteint, ses parents I1 et I2 sont sains. Quel est le génotype des deux parents ?",
                bonne="Tous deux Aa (hétérozygotes porteurs sains)", faux=["Tous deux AA", "I1 aa et I2 AA", "I1 AA et I2 Aa", "Tous deux aa"],
                correction="Un enfant aa reçoit un allèle a de chaque parent ; les parents sains ont donc chacun un A et un a : Aa × Aa.",
                erreurs=["parents supposés non porteurs", "un parent supposé atteint", "un seul parent porteur ne suffit pas", "parents supposés atteints"], figure=fig, legende=leg, rnd=rnd)
        ajouter(id_=f"FIG2-SV-ped-{k}-2", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="difficile", type_item="classique", competence="calculer",
                savoir="Probabilité d'être porteur pour un enfant sain de parents hétérozygotes", famille="document à lire", titre="II2 est-elle porteuse ?",
                tige=f"Pour {mal_art} (anomalie autosomale récessive, arbre ci-contre), II2 est saine et a pour parents I1 et I2, tous deux hétérozygotes puisque leur fils II1 est atteint. Avant son mariage, II2 demande son risque d'être porteuse. Quelle est la probabilité que II2 soit porteuse (Aa) ?",
                bonne="2/3", faux=["1/2", "1/4", "1/3", "3/4"],
                correction="Aa × Aa donne AA, Aa, Aa, aa ; II2 étant saine, elle est AA ou Aa : P(Aa | saine) = 2/3.",
                erreurs=["condition « saine » ignorée", "probabilité de aa", "probabilité de AA parmi les sains", "proportion des phénotypes dominants"], figure=fig, legende=leg, rnd=rnd)
        q = rnd.choice([0.02, 0.05, 0.1])
        ajouter(id_=f"FIG2-SV-ped-{k}-3", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="difficile", type_item="decision", competence="décider",
                savoir="Risque pour l'enfant d'un porteur probable et d'un conjoint de la population générale", famille="décision professionnelle", titre="Faut-il proposer un dépistage au conjoint ?",
                tige=f"II2 (arbre ci-contre, {mal_art} autosomale récessive) épouse II3, sans antécédent ; dans la population, la fréquence des porteurs sains est de {fmt(100 * q, 0)} %. Le médecin propose un test à II3 si le risque pour un enfant dépasse 1 %. Que doit-il faire, et pourquoi ?",
                bonne=(f"Proposer le test, car le risque vaut 2/3 × {fmt(q, 2)} × 1/4 ≈ {fmt(100 * 2 / 3 * q / 4, 2)} %, supérieur à 1 %" if 2 / 3 * q / 4 > 0.01 else f"Ne pas proposer le test, car le risque vaut 2/3 × {fmt(q, 2)} × 1/4 ≈ {fmt(100 * 2 / 3 * q / 4, 2)} %, inférieur à 1 %"),
                faux=[f"{'Ne pas proposer' if 2 / 3 * q / 4 > 0.01 else 'Proposer'} le test, car le risque est de 1/4 comme pour tout couple de porteurs", f"Proposer le test, car II2 est forcément porteuse (2/3 > 1/2)",
                      f"Ne pas proposer le test, car un homme sans antécédent ne peut pas être porteur", f"Proposer le test, car le risque vaut {fmt(100 * q, 0)} %, la fréquence des porteurs"],
                correction=f"Risque = P(II2 Aa) × P(II3 Aa) × P(enfant aa | Aa × Aa) = 2/3 × {fmt(q, 2)} × 1/4 ≈ {fmt(100 * 2 / 3 * q / 4, 2)} %, à comparer au seuil de 1 %.",
                erreurs=["statut des parents supposé certain", "probabilité 2/3 arrondie à certitude", "porteur sans antécédent possible", "fréquence des porteurs confondue avec le risque"], figure=fig, legende=leg, rnd=rnd)


def s_trophique(rnd: random.Random, k: int):
    jeux = [([("h", "herbes aquatiques", 90, 250), ("i", "insectes", 90, 140), ("t", "tilapias", 260, 190), ("hr", "héron", 430, 110), ("c", "crocodile", 430, 250)], [("h", "i"), ("h", "t"), ("i", "t"), ("t", "hr"), ("t", "c"), ("hr", "c")], "un étang"),
            ([("g", "graminées", 90, 250), ("s", "sauterelles", 90, 140), ("l", "lézards", 260, 190), ("o", "oiseaux", 430, 110), ("se", "serpents", 430, 250)], [("g", "s"), ("s", "l"), ("s", "o"), ("l", "se"), ("o", "se")], "une savane"),
            ([("m", "manioc", 90, 250), ("r", "rongeurs", 90, 140), ("ch", "chenilles", 260, 250), ("p", "poules", 260, 120), ("ci", "civette", 430, 190)], [("m", "r"), ("m", "ch"), ("ch", "p"), ("r", "ci"), ("p", "ci")], "un champ")]
    noeuds, fl, milieu = rnd.choice(jeux)
    fig = reseau_trophique(noeuds, fl); leg = f"Réseau trophique observé dans {milieu} (la flèche va du mangé au mangeur)"
    chap = chapitre("SVT", "écosystèmes"); sd = "Écologie"
    nom = {i: l for i, l, _, _ in noeuds}
    prod = [i for i, *_ in noeuds if not any(b == i for a, b in fl)][0]
    sommet = [i for i, *_ in noeuds if not any(a == i for a, b in fl)][0]
    ajouter(id_=f"FIG2-SV-tro-{k}-1", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="facile", type_item="classique", competence="identifier",
            savoir="Producteurs et consommateurs dans un réseau trophique", famille="phénomène observé", titre="Producteur du réseau",
            tige=f"Un agent de l'environnement a schématisé ci-contre les relations alimentaires observées dans {milieu} (chaque flèche va de l'organisme mangé vers celui qui le mange). Quel organisme est le producteur primaire de ce réseau ?",
            bonne=nom[prod].capitalize(), faux=[nom[i].capitalize() for i in nom if i != prod][:4],
            correction=f"Le producteur est l'organisme qui ne mange personne et fabrique sa matière par photosynthèse : {nom[prod]}, à l'origine de toutes les chaînes.",
            erreurs=["consommateur pris pour producteur", "consommateur pris pour producteur", "superprédateur pris pour producteur", "consommateur pris pour producteur"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-SV-tro-{k}-2", discipline="SVT", sous=sd, epreuve="M.46", chap=chap, difficulte="moyen", type_item="classique", competence="interpréter",
            savoir="Niveaux trophiques multiples d'un même organisme", famille="phénomène observé", titre="Superprédateur du réseau",
            tige=f"Dans le réseau trophique ci-contre, observé dans {milieu}, l'agent de l'environnement doit désigner le superprédateur pour son rapport. Quel organisme occupe le sommet du réseau, c'est-à-dire n'est mangé par aucun autre et peut appartenir à plusieurs niveaux de consommateurs selon la chaîne suivie ?",
            bonne=nom[sommet].capitalize(), faux=[nom[i].capitalize() for i in nom if i != sommet][:4],
            correction=f"Aucune flèche ne part de « {nom[sommet]} » : il n'est mangé par personne. Selon la chaîne suivie, il est consommateur de niveaux différents.",
            erreurs=["organisme mangé par un autre", "producteur", "consommateur intermédiaire", "consommateur intermédiaire"], figure=fig, legende=leg, rnd=rnd)
    victime = rnd.choice([i for i, *_ in noeuds if i not in (prod, sommet)])
    mange = [nom[b] for a, b in fl if a == victime]
    ajouter(id_=f"FIG2-SV-tro-{k}-3", discipline="SVT", sous=sd, epreuve="M.46", chap=chapitre("SVT", "interdépendance", "écosystèmes"), difficulte="moyen", type_item="decision", competence="décider",
            savoir="Conséquences de la disparition d'un maillon sur un réseau trophique", famille="décision professionnelle", titre="Faut-il autoriser l'élimination d'une espèce ?",
            tige=f"Des habitants, gênés par leur présence, demandent l'élimination complète des {nom[victime]} {('de l' + chr(39)) if milieu.startswith('un é') else ('du ' if milieu.startswith('un ') else 'de la ')}{milieu.split(' ', 1)[1]} dont le réseau trophique est schématisé ci-contre. L'agent de l'environnement est chargé de donner un avis motivé avant toute campagne. Que doit-il répondre, et pourquoi ?",
            bonne=f"Refuser, car les {nom[victime]} nourrissent {' et '.join(mange)} : leur disparition réduit ces populations et déséquilibre le réseau",
            faux=[f"Accepter, car les {nom[victime]} ne sont pas producteurs et le réseau n'en dépend pas", f"Accepter, car {' et '.join(mange)} trouveront toujours une autre proie en quantité suffisante",
                  f"Refuser, car les {nom[victime]} sont le producteur primaire du réseau", f"Accepter, car la disparition d'une espèce fait toujours augmenter toutes les autres"],
            correction=f"Les flèches partant de « {nom[victime]} » montrent qu'ils sont mangés par {' et '.join(mange)} ; supprimer un maillon réduit ses prédateurs et peut faire proliférer ce qu'il mangeait : interdépendance des espèces.",
            erreurs=["rôle du maillon nié", "substitution supposée sans limite", "producteur confondu", "effet inverse"], figure=fig, legende=leg, rnd=rnd)


# ======================================================================================================================
GABARITS = {
    "Mathématiques": [m_exp, m_batons, m_aire, m_arbre, m_complexe],
    "Physique": [p_vt, p_circuit, p_incline, p_oscillo, p_transfo, p_lentille],
    "Chimie": [c_dosage, c_radio, c_chromato, c_dilution, c_atome],
    "SVT": [s_logistique, s_punnett, s_pedigree, s_trophique],
}


def produire(variantes: int, graine: int = 2026) -> list[dict]:
    ITEMS.clear()
    for disc, gens in GABARITS.items():
        for g in gens:
            for k in range(1, variantes + 1):
                rnd = random.Random(f"{graine}-{g.__name__}-{k}")
                g(rnd, k)
    return list(ITEMS)
