"""Générateurs de questions à figures — Géographie, Électricité, Mécanique appliquée, Statistique, Démographie,
Organisation des entreprises (matières transversales à de nombreuses épreuves du E.32)."""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from figures import ENCRE, GRILLE, GRIS, NUIT, OR, ROUGE, VERT, Plot, circuit_serie, pie, svg, table, txt  # noqa: E402
from outils import chapitre, fmt, item  # noqa: E402

ITEMS: list[dict] = []


def fc(v) -> str:
    """Montant en FC avec séparateur de milliers."""
    return f"{int(round(v)):,}".replace(",", " ")

SAUTES: list[str] = []


def ajouter(**kw):
    try:
        ITEMS.append(item(**kw))
    except AssertionError as e:
        SAUTES.append(str(e)[:120])


MOIS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
MOIS_NOMS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


# ------------------------------------------------------------------ figures propres à ce module

def climatogramme(precip: list, temp: list, w=520, h=320) -> str:
    pmax = max(precip) * 1.15
    p = Plot(0.3, 12.7, 0, pmax, w, h, ml=52, mr=60, xstep=1, ystep=50 if pmax > 150 else 25, xlabel="mois", ylabel="P (mm)", grid=False, xfmt=lambda v: MOIS[int(round(v)) - 1] if 1 <= round(v) <= 12 else "")
    p.bars([(i + 1, v) for i, v in enumerate(precip)], 0.6, color="#6C8EBF", labels=False)
    # température sur un second axe à l'échelle P = 2T (40 °C en face de 80 mm)
    Yt = lambda t: p.Y(2 * t)
    pts = " ".join(f"{p.X(i + 1):.1f},{Yt(t):.1f}" for i, t in enumerate(temp))
    p.parts.append(f"<polyline fill='none' stroke='{ROUGE}' stroke-width='2.4' points='{pts}'/>")
    for i, t in enumerate(temp):
        p.parts.append(f"<circle cx='{p.X(i + 1):.1f}' cy='{Yt(t):.1f}' r='3' fill='{ROUGE}'/>")
    xr = p.w - p.mr + 6
    for t in (0, 10, 20, 30, 40):
        p.parts.append(f"<line x1='{xr - 4}' y1='{Yt(t):.1f}' x2='{xr + 4}' y2='{Yt(t):.1f}' stroke='{ROUGE}'/>")
        p.parts.append(txt(xr + 8, Yt(t) + 4, str(t), 11, "start", ROUGE))
    p.parts.append(f"<line x1='{xr}' y1='{p.h - p.mb}' x2='{xr}' y2='{Yt(40):.1f}' stroke='{ROUGE}' stroke-width='1.4'/>")
    p.parts.append(txt(xr + 8, Yt(40) - 12, "T (°C)", 12, "start", ROUGE, italic=True))
    return p.render()


def pyramide(ages: list, hommes: list, femmes: list, w=520, h=340) -> str:
    """ages : libellés des tranches (bas vers haut) ; effectifs en milliers ou en %."""
    mx = max(max(hommes), max(femmes)) * 1.1
    n = len(ages); cx = w / 2; top, bot = 30, h - 40
    bh = (bot - top) / n
    sc = (w / 2 - 70) / mx
    out = [txt(cx - 90, 20, "Hommes", 13, "middle", NUIT, "bold"), txt(cx + 90, 20, "Femmes", 13, "middle", ROUGE, "bold")]
    for i, (a, hm, fm) in enumerate(zip(ages, hommes, femmes)):
        y = bot - (i + 1) * bh
        out.append(f"<rect x='{cx - 30 - hm * sc:.1f}' y='{y + 2:.1f}' width='{hm * sc:.1f}' height='{bh - 4:.1f}' fill='{NUIT}' fill-opacity='0.8'/>")
        out.append(f"<rect x='{cx + 30:.1f}' y='{y + 2:.1f}' width='{fm * sc:.1f}' height='{bh - 4:.1f}' fill='{ROUGE}' fill-opacity='0.75'/>")
        out.append(txt(cx, y + bh / 2 + 4, a, 11))
        out.append(txt(cx - 34 - hm * sc, y + bh / 2 + 4, fmt(hm), 10, "end", GRIS))
        out.append(txt(cx + 34 + fm * sc, y + bh / 2 + 4, fmt(fm), 10, "start", GRIS))
    out.append(txt(cx, h - 12, "effectifs en milliers", 11, "middle", GRIS, italic=True))
    return svg(w, h, "".join(out))


def poutre(L: float, a: float, F: float, w=520, h=220) -> str:
    """Poutre sur deux appuis A (gauche) et B (droite), charge ponctuelle F à la distance a de A."""
    x0, x1, y = 60, w - 60, 110
    X = lambda d: x0 + (x1 - x0) * d / L
    out = [f"<defs><marker id='fp' markerWidth='8' markerHeight='8' refX='6' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='{ROUGE}'/></marker></defs>",
           f"<rect x='{x0}' y='{y - 8}' width='{x1 - x0}' height='16' fill='#E8E2D3' stroke='{NUIT}' stroke-width='1.8'/>",
           f"<polygon points='{x0},{y + 8} {x0 - 14},{y + 34} {x0 + 14},{y + 34}' fill='{NUIT}'/>", f"<polygon points='{x1},{y + 8} {x1 - 14},{y + 34} {x1 + 14},{y + 34}' fill='{NUIT}'/>",
           f"<circle cx='{x1}' cy='{y + 40}' r='5' fill='none' stroke='{NUIT}' stroke-width='1.5'/>",
           txt(x0, y + 52, "A", 13, weight="bold"), txt(x1, y + 56, "B", 13, weight="bold"),
           f"<line x1='{X(a):.1f}' y1='{y - 70}' x2='{X(a):.1f}' y2='{y - 12}' stroke='{ROUGE}' stroke-width='2.6' marker-end='url(#fp)'/>",
           txt(X(a) + 10, y - 50, f"F = {fmt(F)} kN", 13, "start", ROUGE, "bold"),
           f"<line x1='{x0}' y1='{y + 70}' x2='{X(a):.1f}' y2='{y + 70}' stroke='{ENCRE}'/>", txt((x0 + X(a)) / 2, y + 86, f"a = {fmt(a)} m", 12),
           f"<line x1='{X(a):.1f}' y1='{y + 70}' x2='{x1}' y2='{y + 70}' stroke='{ENCRE}'/>", txt((X(a) + x1) / 2, y + 86, f"b = {fmt(L - a)} m", 12),
           f"<line x1='{X(a):.1f}' y1='{y + 62}' x2='{X(a):.1f}' y2='{y + 78}' stroke='{ENCRE}'/>",
           f"<line x1='{x0}' y1='{y + 62}' x2='{x0}' y2='{y + 78}' stroke='{ENCRE}'/>", f"<line x1='{x1}' y1='{y + 62}' x2='{x1}' y2='{y + 78}' stroke='{ENCRE}'/>",
           txt(w / 2, y + 104, f"L = {fmt(L)} m", 12, color=GRIS)]
    return svg(w, h, "".join(out))


def circuit_parallele(R1, R2, U, w=460, h=240) -> str:
    L, R_, T, B = 70, w - 70, 50, h - 50
    xm1, xm2 = L + (R_ - L) * 0.45, L + (R_ - L) * 0.75
    out = [f"<rect x='{L}' y='{T}' width='{R_ - L}' height='{B - T}' fill='none' stroke='{NUIT}' stroke-width='1.8'/>",
           f"<line x1='{xm1}' y1='{T}' x2='{xm1}' y2='{B}' stroke='{NUIT}' stroke-width='1.8'/>"]
    for x, lab in ((xm1, f"R₁ = {R1} Ω"), (R_, f"R₂ = {R2} Ω")):
        ym = (T + B) / 2
        out.append(f"<rect x='{x - 8}' y='{ym - 22}' width='16' height='44' fill='#fff' stroke='{NUIT}' stroke-width='1.8'/>")
        out.append(txt(x + 14, ym + 4, lab, 12, "start"))
    ym = (T + B) / 2
    out.append(f"<rect x='{L - 18}' y='{ym - 20}' width='36' height='40' fill='#fff'/>")
    out.append(f"<line x1='{L - 14}' y1='{ym - 4}' x2='{L + 14}' y2='{ym - 4}' stroke='{NUIT}' stroke-width='3'/><line x1='{L - 8}' y1='{ym + 4}' x2='{L + 8}' y2='{ym + 4}' stroke='{NUIT}' stroke-width='1.6'/>")
    out.append(txt(L, B + 24, f"U = {U} V", 12))
    out.append(f"<circle cx='{(L + xm1) / 2}' cy='{T}' r='13' fill='#fff' stroke='{NUIT}' stroke-width='1.8'/>" + txt((L + xm1) / 2, T + 5, "A", 13, weight="bold"))
    return svg(w, h, "".join(out))


# ======================================================================================================================
# GÉOGRAPHIE (M.01 et autres culture générale)
# ======================================================================================================================

CLIMATS = {
    "équatorial": ([150, 140, 180, 190, 160, 120, 90, 110, 170, 200, 210, 170], [26, 26, 26, 26, 26, 25, 24, 25, 26, 26, 26, 26]),
    "tropical humide": ([120, 110, 160, 180, 150, 40, 15, 30, 110, 190, 200, 150], [26, 27, 27, 26, 26, 24, 23, 24, 25, 26, 26, 26]),
    "tropical à longue saison sèche": ([200, 170, 150, 80, 20, 5, 2, 10, 60, 130, 190, 210], [27, 27, 26, 25, 23, 21, 20, 22, 25, 27, 27, 27]),
    "d'altitude": ([110, 100, 130, 150, 120, 40, 20, 40, 90, 160, 170, 130], [19, 19, 19, 19, 19, 18, 17, 18, 19, 19, 19, 19]),
}


def g_climato(rnd: random.Random, k: int):
    nom, (pr, tp) = rnd.choice(list(CLIMATS.items()))
    pr = [max(0, v + rnd.randint(-15, 15)) for v in pr]; tp = [t + rnd.choice([-1, 0, 1]) for t in tp]
    fig = climatogramme(pr, tp); leg = "Diagramme ombrothermique d'une station (barres : précipitations ; courbe : températures)"
    total = sum(pr); secs = sum(1 for v, t in zip(pr, tp) if v < 2 * t); ampl = max(tp) - min(tp)
    ville = rnd.choice(["Mbandaka", "Kikwit", "Lubumbashi", "Bukavu", "Kananga", "Kisangani", "Kalemie", "Goma"])
    chap = chapitre("Géographie", "climat")
    ajouter(id_=f"FIG2-GE-cli-{k}-1", discipline="Géographie", sous=None, epreuve="M.01", chap=chap, difficulte="facile", type_item="classique", competence="interpréter",
            savoir="Lecture d'un diagramme ombrothermique : mois secs (P < 2T)", famille="donnée brute", titre="Mois secs d'une station",
            tige=f"Le service météorologique a tracé le diagramme ombrothermique ci-contre pour une station de la région de {ville} (barres : précipitations en mm ; courbe rouge : températures en °C). "
                 f"Un mois est dit sec quand P < 2T. Combien de mois secs compte cette station ?",
            bonne=f"{secs}", faux=[f"{secs + 2}", f"{max(0, secs - 2) if secs >= 2 else secs + 4}", f"{secs + 1 if secs + 1 not in (secs + 2,) else secs + 3}", f"{12 - secs if 12 - secs not in (secs, secs + 1, secs + 2) else 6 if 6 not in (secs, secs + 1, secs + 2) else 7}"],
            correction=f"Avec l'échelle P = 2T (0–40 °C face à 0–80 mm), un mois est sec quand la barre passe sous la courbe : {secs} mois ({', '.join(MOIS_NOMS[i] for i, (v, t) in enumerate(zip(pr, tp)) if v < 2 * t) or 'aucun'}).",
            erreurs=["mois humides comptés en partie", "lecture approximative", "critère P < T utilisé", "mois humides comptés"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-GE-cli-{k}-2", discipline="Géographie", sous=None, epreuve="M.01", chap=chap, difficulte="moyen", type_item="classique", competence="identifier",
            savoir="Identification d'un type de climat à partir du régime des pluies et de l'amplitude thermique", famille="donnée brute", titre="Type de climat",
            tige=f"Un étudiant en géographie doit classer la station de {ville} dont le diagramme ombrothermique est donné ci-contre : total annuel ≈ {total} mm, amplitude thermique {ampl} °C, {secs} mois sec(s) au sens de P < 2T. À quel type de climat appartient cette station ?",
            bonne=f"Climat {nom}", faux=[f"Climat {n}" for n in CLIMATS if n != nom][:3] + ["Climat méditerranéen"],
            correction=f"{total} mm par an, {secs} mois sec(s) et une amplitude de {ampl} °C caractérisent un climat {nom} ({'pluies toute l année, chaleur constante' if nom == 'équatorial' else 'saison sèche marquée' if 'sèche' in nom else 'saison sèche courte' if 'humide' in nom else 'températures modérées par l altitude'}).",
            erreurs=["régime des pluies mal lu", "saison sèche mal évaluée", "températures mal lues", "climat absent de la RDC"], figure=fig, legende=leg, rnd=rnd)
    culture = rnd.choice([("le maïs", 4, "quatre mois consécutifs à plus de 80 mm"), ("le riz pluvial", 5, "cinq mois consécutifs à plus de 100 mm"), ("le haricot", 3, "trois mois consécutifs à plus de 60 mm")])
    seuil = {4: 80, 5: 100, 3: 60}[culture[1]]
    best = 0; cur = 0
    for v in pr + pr[:culture[1]]:
        cur = cur + 1 if v > seuil else 0
        best = max(best, cur)
    ok = best >= culture[1]
    ajouter(id_=f"FIG2-GE-cli-{k}-3", discipline="Géographie", sous=None, epreuve="M.01", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Calendrier agricole déduit d'un diagramme ombrothermique", famille="décision professionnelle", titre="Peut-on cultiver sans irrigation ?",
            tige=f"Un agronome doit dire si {culture[0]} peut être cultivé sans irrigation près de cette station (diagramme ci-contre) ; la culture exige {culture[2]}. Que doit-il conclure, et pourquoi ?",
            bonne=(f"Oui, car on trouve {best} mois consécutifs au-dessus de {seuil} mm, assez pour le cycle" if ok else f"Non sans irrigation, car la plus longue suite de mois au-dessus de {seuil} mm ne compte que {best} mois"),
            faux=[(f"Non, car le total annuel {total} mm est insuffisant" if ok else f"Oui, car le total annuel {total} mm suffit largement"), f"Oui, car la température moyenne dépasse toujours 15 °C", f"Non, car il y a {secs} mois secs dans l'année", f"Oui, car le mois le plus arrosé reçoit {max(pr)} mm"],
            correction=f"Il faut lire la succession des mois : la plus longue série de mois à plus de {seuil} mm compte {best} mois, {'au moins' if ok else 'moins que'} les {culture[1]} requis. Le total annuel ou le maximum mensuel ne garantissent pas la continuité.",
            erreurs=["total annuel pris pour critère", "température seule", "nombre de mois secs sans regarder la saison", "maximum mensuel"], figure=fig, legende=leg, rnd=rnd)


def g_pyramide(rnd: random.Random, k: int, discipline="Géographie", epreuve="M.01"):
    jeune = rnd.random() < 0.6
    ages = ["0-14", "15-29", "30-44", "45-59", "60-74", "75+"]
    if jeune:
        h = [rnd.randint(380, 460), rnd.randint(260, 330), rnd.randint(170, 220), rnd.randint(90, 130), rnd.randint(40, 60), rnd.randint(10, 20)]
    else:
        h = [rnd.randint(150, 190), rnd.randint(190, 230), rnd.randint(220, 260), rnd.randint(200, 240), rnd.randint(140, 180), rnd.randint(70, 100)]
    f = [v + rnd.randint(-15, 25) for v in h]
    fig = pyramide(ages, h, f); leg = "Pyramide des âges d'une province (effectifs en milliers)"
    tot = sum(h) + sum(f); part_j = 100 * (h[0] + f[0]) / tot; part_v = 100 * (h[4] + h[5] + f[4] + f[5]) / tot
    prov = rnd.choice(["Kwilu", "Haut-Katanga", "Nord-Kivu", "Kasaï-Central", "Tshopo", "Kongo-Central", "Équateur", "Maniema"])
    chap = chapitre(discipline, "population", "démographie") if discipline == "Géographie" else chapitre(discipline, "structure", "pyramide")
    ajouter(id_=f"FIG2-{'GE' if discipline == 'Géographie' else 'DE'}-pyr-{k}-1", discipline=discipline, sous=None, epreuve=epreuve, chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Part des jeunes dans une pyramide des âges", famille="document à lire", titre="Part des moins de 15 ans",
            tige=f"La pyramide des âges ci-contre résume le recensement de la province du {prov} (effectifs en milliers, hommes à gauche, femmes à droite). Un planificateur doit calculer la part des moins de 15 ans dans la population totale. Quelle valeur, arrondie à l'unité, obtient-il ?",
            bonne=f"{fmt(part_j, 0)} %", faux=[f"{fmt(100 * h[0] / tot, 0)} %", f"{fmt(100 * (h[0] + f[0]) / (sum(h)), 0)} %", f"{fmt(part_v, 0)} %", f"{fmt(part_j / 2, 0)} %"],
            correction=f"Moins de 15 ans : {h[0]} + {f[0]} = {h[0] + f[0]} milliers ; population totale {tot} milliers ; part = {h[0] + f[0]}/{tot} ≈ {fmt(part_j, 0)} %.",
            erreurs=["hommes seulement au numérateur", "dénominateur limité aux hommes", "part des 60 ans et plus", "division par 2 injustifiée"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-{'GE' if discipline == 'Géographie' else 'DE'}-pyr-{k}-2", discipline=discipline, sous=None, epreuve=epreuve, chap=chap, difficulte="moyen", type_item="classique", competence="interpréter",
            savoir="Forme d'une pyramide des âges et dynamique démographique", famille="document à lire", titre="Lecture de la forme de la pyramide",
            tige=f"Un journaliste commente la pyramide des âges de la province du {prov} reproduite ci-contre (effectifs en milliers). Il observe une base {'très large et un sommet étroit' if jeune else 'plus étroite que les tranches d âge intermédiaires'}. Quelle dynamique démographique cette forme traduit-elle pour la province ?",
            bonne=("Natalité élevée et population jeune, en croissance rapide" if jeune else "Natalité en baisse et population vieillissante, croissance ralentie"),
            faux=[("Natalité en baisse et population vieillissante" if jeune else "Natalité élevée et population très jeune"), "Mortalité infantile nulle", "Population stable sans naissances ni décès", "Forte immigration de personnes âgées"],
            correction=("Une base large (nombreux enfants) et un sommet étroit (peu de personnes âgées) caractérisent une population jeune à forte natalité, typique de la RDC." if jeune else "Une base rétrécie indique une baisse récente des naissances ; les tranches adultes dominantes et un sommet élargi traduisent un vieillissement."),
            erreurs=["lecture inversée", "mortalité infantile non lisible ici", "stabilité contredite par la forme", "migration non déductible"], figure=fig, legende=leg, rnd=rnd)
    places = rnd.choice([30, 40, 50]); ecoles = math.ceil((h[0] + f[0]) * 1000 * 0.6 / places / 6 / 10) * 10  # 60 % scolarisables au primaire, 6 classes par école
    ajouter(id_=f"FIG2-{'GE' if discipline == 'Géographie' else 'DE'}-pyr-{k}-3", discipline=discipline, sous=None, epreuve=epreuve, chap=chap, difficulte="difficile", type_item="decision", competence="décider",
            savoir="Planification de services à partir de la structure par âge", famille="décision professionnelle", titre="Combien de salles de classe prévoir ?",
            tige=f"Le planificateur du {prov} estime que 60 % des moins de 15 ans ({h[0] + f[0]} milliers d'après la pyramide ci-contre) relèvent du primaire, à {places} élèves par classe. Il doit annoncer un ordre de grandeur du nombre de classes nécessaires. Quelle annonce est correcte, et pourquoi ?",
            bonne=f"Environ {fmt((h[0] + f[0]) * 1000 * 0.6 / places, 0)} classes, car 60 % de {h[0] + f[0]} 000 élèves divisés par {places} par classe",
            faux=[f"Environ {fmt((h[0] + f[0]) * 1000 / places, 0)} classes, car tous les moins de 15 ans sont à scolariser", f"Environ {fmt((h[0] + f[0]) * 0.6 / places, 0)} classes, car les effectifs se lisent directement",
                  f"Environ {fmt(tot * 1000 * 0.6 / places, 0)} classes, car toute la population doit être prise en compte", f"Environ {fmt((h[0]) * 1000 * 0.6 / places, 0)} classes, car seuls les garçons sont comptés"],
            correction=f"Élèves du primaire ≈ 0,6 × {h[0] + f[0]} 000 = {fmt((h[0] + f[0]) * 600, 0)} ; classes ≈ {fmt((h[0] + f[0]) * 600, 0)}/{places} ≈ {fmt((h[0] + f[0]) * 1000 * 0.6 / places, 0)}.",
            erreurs=["taux de 60 % oublié", "milliers oubliés", "population totale utilisée", "filles oubliées"], figure=fig, legende=leg, rnd=rnd)


def g_evolution(rnd: random.Random, k: int):
    an0 = rnd.choice([2000, 2004, 2008]); n = 5; v0 = rnd.choice([40, 60, 80, 100, 150]); taux = rnd.choice([0.02, 0.03, 0.035, 0.05])
    vals = [v0 * (1 + taux) ** (4 * i) for i in range(n)]
    p = Plot(an0 - 2, an0 + 4 * (n - 1) + 2, 0, max(vals) * 1.2, 460, 300, xstep=4, ystep=20 if max(vals) < 150 else 50, xlabel="année", ylabel="habitants (milliers)", xfmt=lambda v: str(int(round(v))), yfmt=lambda v: fmt(round(v)))
    p.polyline([(an0 + 4 * i, v) for i, v in enumerate(vals)], NUIT, 2.4)
    for i, v in enumerate(vals):
        p.point(an0 + 4 * i, v, fmt(round(v)), dx=0, dy=-10, anchor="middle")
    fig, leg = p.render(), "Évolution de la population d'une ville (milliers d'habitants)"
    ville = rnd.choice(["Kikwit", "Bunia", "Uvira", "Gemena", "Kindu", "Tshikapa", "Butembo"])
    croiss = 100 * (vals[-1] / vals[0] - 1); tx_an = 100 * ((vals[-1] / vals[0]) ** (1 / (4 * (n - 1))) - 1)
    chap = chapitre("Géographie", "population", "démographie")
    ajouter(id_=f"FIG2-GE-evo-{k}-1", discipline="Géographie", sous=None, epreuve="M.01", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Taux de croissance global sur une période", famille="donnée brute", titre="Croissance d'une ville",
            tige=f"Le graphique ci-contre donne la population de {ville} tous les quatre ans entre {an0} et {an0 + 4 * (n - 1)} (milliers d'habitants). De quel pourcentage la population a-t-elle augmenté sur toute la période ?",
            bonne=f"{fmt(croiss, 0)} %", faux=[f"{fmt(vals[-1] - vals[0], 0)} %", f"{fmt(tx_an, 1)} %", f"{fmt(croiss / (4 * (n - 1)), 1)} %", f"{fmt(100 * (1 - vals[0] / vals[-1]), 0)} %"],
            correction=f"({fmt(round(vals[-1]))} − {fmt(round(vals[0]))})/{fmt(round(vals[0]))} × 100 ≈ {fmt(croiss, 0)} %.",
            erreurs=["différence absolue prise pour un pourcentage", "taux annuel", "taux moyen par an", "base finale au dénominateur"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-GE-evo-{k}-2", discipline="Géographie", sous=None, epreuve="M.01", chap=chap, difficulte="moyen", type_item="classique", competence="interpréter",
            savoir="Taux de croissance annuel moyen", famille="donnée brute", titre="Rythme annuel de croissance",
            tige=f"D'après le graphique ci-contre ({ville}, {an0}–{an0 + 4 * (n - 1)}), un urbaniste veut connaître le taux de croissance annuel moyen de la population, en pourcentage arrondi au dixième. Quelle valeur est correcte ?",
            bonne=f"{fmt(tx_an, 1)} %", faux=[f"{fmt(croiss / (n - 1), 1)} %", f"{fmt(croiss, 0)} %", f"{fmt(croiss / (4 * (n - 1)) * 1.6, 1)} %", f"{fmt(tx_an * 4, 1)} %"],
            correction=f"Le taux annuel r vérifie {fmt(round(vals[0]))}(1 + r)^{4 * (n - 1)} = {fmt(round(vals[-1]))} ⇒ r = ({fmt(vals[-1] / vals[0], 3)})^(1/{4 * (n - 1)}) − 1 ≈ {fmt(tx_an, 1)} % par an (proche de {fmt(croiss / (4 * (n - 1)), 1)} % en approximation linéaire).",
            erreurs=["division par le nombre de points", "taux global", "approximation linéaire fausse", "taux quadriennal"], figure=fig, legende=leg, rnd=rnd)
    cap = round(vals[-1] * rnd.choice([1.1, 1.3, 1.6]) / 10) * 10
    annees = math.log(cap / vals[-1]) / math.log(1 + taux)
    ajouter(id_=f"FIG2-GE-evo-{k}-3", discipline="Géographie", sous=None, epreuve="M.01", chap=chap, difficulte="difficile", type_item="decision", competence="décider",
            savoir="Projection démographique et capacité d'un équipement", famille="décision professionnelle", titre="La station d'eau suffira-t-elle ?",
            tige=f"La station de traitement d'eau de {ville} est dimensionnée pour {cap} milliers d'habitants. Si la croissance du graphique ci-contre ({fmt(tx_an, 1)} % par an) se poursuit, le gestionnaire doit décider s'il lance l'extension maintenant (délai de travaux : 5 ans). Que doit-il décider, et pourquoi ?",
            bonne=(f"Lancer l'extension maintenant, car la capacité sera atteinte dans environ {fmt(annees, 0)} ans, moins que le délai de 5 ans" if annees <= 5 else f"Différer l'extension, car la capacité ne sera atteinte que dans environ {fmt(annees, 0)} ans, au-delà du délai de 5 ans"),
            faux=[(f"Différer, car la population actuelle {fmt(round(vals[-1]))} est inférieure à {cap}" if annees <= 5 else f"Lancer maintenant, car la population croît chaque année"),
                  f"Lancer maintenant, car en 5 ans la population augmente de {fmt(5 * tx_an, 0)} %, donc dépasse {cap}" if vals[-1] * (1 + 5 * tx_an / 100) < cap else f"Différer, car {fmt(5 * tx_an, 0)} % en 5 ans ne suffisent pas à atteindre {cap}",
                  f"Différer, car la croissance ralentit toujours après {an0 + 4 * (n - 1)}", f"Lancer maintenant, car la station ne peut servir que {cap - round(vals[-1])} milliers d'habitants"],
            correction=f"Années avant d'atteindre {cap} : ln({cap}/{fmt(round(vals[-1]))})/ln(1 + {fmt(taux, 3)}) ≈ {fmt(annees, 1)} ans, à comparer au délai de 5 ans.",
            erreurs=["situation actuelle sans projection", "approximation linéaire trompeuse", "ralentissement supposé", "marge mal interprétée"], figure=fig, legende=leg, rnd=rnd)


# ======================================================================================================================
# ÉLECTRICITÉ (options techniques) — alias « Électricité générale », « Électricité industrielle »
# ======================================================================================================================

def e_parallele(rnd: random.Random, k: int, discipline="Électricité"):
    U = rnd.choice([12, 24, 48, 220]); R1 = rnd.choice([10, 20, 30, 40, 60]); R2 = rnd.choice([20, 30, 60, 120])
    Req = R1 * R2 / (R1 + R2); I = U / Req; I1 = U / R1; P = U * I
    fig = circuit_parallele(R1, R2, U); leg = "Deux résistances en parallèle sous une source continue"
    chap = chapitre(discipline, "protection", "réseaux")
    ctx = rnd.choice(["l'éclairage d'un atelier de couture", "le tableau d'une pompe de forage", "un panneau solaire de dispensaire", "le circuit d'une chambre froide"])
    ajouter(id_=f"FIG2-EL-par-{k}-1", discipline=discipline, sous=None, epreuve="M.80", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Résistance équivalente de deux résistances en parallèle", famille="document technique", titre="Résistance équivalente en parallèle",
            tige=f"Le schéma ci-contre, relevé sur {ctx}, montre R₁ = {R1} Ω et R₂ = {R2} Ω montées en parallèle sous U = {U} V. Quelle est la résistance équivalente du groupement ?",
            bonne=f"{fmt(Req, 2)} Ω", faux=[f"{fmt(R1 + R2, 2)} Ω", f"{fmt((R1 + R2) / 2, 2)} Ω", f"{fmt(R1 * R2, 2)} Ω", f"{fmt(abs(R1 - R2) or R1, 2)} Ω"],
            correction=f"1/R_eq = 1/R₁ + 1/R₂ ⇒ R_eq = R₁R₂/(R₁ + R₂) = {R1}×{R2}/{R1 + R2} = {fmt(Req, 2)} Ω, inférieure à la plus petite des deux.",
            erreurs=["somme (montage série)", "moyenne", "produit seul", "différence"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-EL-par-{k}-2", discipline=discipline, sous=None, epreuve="M.80", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Loi des nœuds : intensité totale et intensités de branche", famille="document technique", titre="Intensité totale débitée",
            tige=f"Dans le montage parallèle ci-contre (U = {U} V, R₁ = {R1} Ω, R₂ = {R2} Ω), l'ampèremètre placé sur le fil principal mesure l'intensité totale. Quelle valeur indique-t-il ?",
            bonne=f"{fmt(I, 2)} A", faux=[f"{fmt(I1, 2)} A", f"{fmt(U / (R1 + R2), 2)} A", f"{fmt(U / R2, 2)} A", f"{fmt(I / 2, 2)} A"],
            correction=f"I₁ = U/R₁ = {fmt(I1, 2)} A ; I₂ = U/R₂ = {fmt(U / R2, 2)} A ; loi des nœuds : I = I₁ + I₂ = {fmt(I, 2)} A (= U/R_eq).",
            erreurs=["une seule branche", "résistances additionnées", "seconde branche seule", "moitié injustifiée"], figure=fig, legende=leg, rnd=rnd)
    disj = rnd.choice([2, 4, 6, 10, 16])
    ajouter(id_=f"FIG2-EL-par-{k}-3", discipline=discipline, sous=None, epreuve="M.80", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Choix du calibre d'un disjoncteur sur un circuit parallèle", famille="décision professionnelle", titre="Le disjoncteur convient-il ?",
            tige=f"Pour {ctx} (schéma ci-contre, U = {U} V, R₁ = {R1} Ω, R₂ = {R2} Ω), l'électricien dispose d'un disjoncteur de {disj} A à placer sur le fil principal. Peut-il l'utiliser, et pourquoi ?",
            bonne=(f"Oui, car l'intensité totale U/R₁ + U/R₂ = {fmt(I, 2)} A reste sous {disj} A" if I <= disj else f"Non, car l'intensité totale U/R₁ + U/R₂ = {fmt(I, 2)} A dépasse {disj} A"),
            faux=[(f"Non, car {fmt(I1, 2)} A + {fmt(U / R2, 2)} A font plus de {disj} A" if I <= disj else f"Oui, car chaque branche ({fmt(I1, 2)} A et {fmt(U / R2, 2)} A) reste sous {disj} A") if True else "",
                  f"{'Oui' if U / (R1 + R2) <= disj else 'Non'}, car U/(R₁ + R₂) = {fmt(U / (R1 + R2), 2)} A", f"Oui, car la tension {U} V est inférieure au calibre", f"Non, car en parallèle l'intensité se divise et le disjoncteur ne voit que la moitié"],
            correction=f"Le fil principal porte la somme des intensités de branche : {fmt(I1, 2)} + {fmt(U / R2, 2)} = {fmt(I, 2)} A, {'inférieure' if I <= disj else 'supérieure'} au calibre {disj} A.",
            erreurs=["branches considérées séparément", "résistances additionnées comme en série", "tension comparée à une intensité", "division mal comprise"], figure=fig, legende=leg, rnd=rnd)


def e_facture(rnd: random.Random, k: int, discipline="Électricité"):
    apps = rnd.sample([("Réfrigérateur", 150, 24), ("Téléviseur", 80, 5), ("Fer à repasser", 1000, 1), ("Lampes LED (6)", 60, 6), ("Ventilateur", 70, 8), ("Congélateur", 200, 24), ("Bouilloire", 1500, 0.5), ("Ordinateur", 120, 6)], 4)
    rows = [[a, f"{p} W", f"{fmt(h)} h/jour", f"{fmt(p * h / 1000, 2)} kWh"] for a, p, h in apps]
    fig = table(["Appareil", "Puissance", "Usage", "Énergie / jour"], rows, col_w=[130, 90, 100, 110], first_col_bold=True); leg = "Relevé des appareils d'un ménage"
    ej = sum(p * h / 1000 for _, p, h in apps); prix = rnd.choice([120, 150, 180, 200])
    chap = chapitre(discipline, "production", "transport", "énergie")
    ajouter(id_=f"FIG2-EL-fac-{k}-1", discipline=discipline, sous=None, epreuve="M.80", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Énergie électrique E = P·t et consommation mensuelle", famille="document à lire", titre="Consommation mensuelle d'un ménage",
            tige=f"Le relevé ci-contre, dressé par un agent de la SNEL chez un abonné, donne la puissance et la durée d'usage quotidienne de chaque appareil. Quelle est la consommation mensuelle (30 jours) du ménage, arrondie au kWh ?",
            bonne=f"{fmt(ej * 30, 0)} kWh", faux=[f"{fmt(ej, 1)} kWh", f"{fmt(sum(p for _, p, _ in apps) * 30 / 1000, 0)} kWh", f"{fmt(ej * 30 * 1000, 0)} kWh", f"{fmt(ej * 24, 0)} kWh"],
            correction=f"Énergie par jour : {' + '.join(fmt(p * h / 1000, 2) for _, p, h in apps)} = {fmt(ej, 2)} kWh ; par mois : {fmt(ej, 2)} × 30 ≈ {fmt(ej * 30, 0)} kWh.",
            erreurs=["consommation d'un seul jour", "puissances additionnées sans durée", "unité Wh au lieu de kWh", "24 jours au lieu de 30"], figure=fig, legende=leg, rnd=rnd)
    gros = max(apps, key=lambda a: a[1] * a[2])
    ajouter(id_=f"FIG2-EL-fac-{k}-2", discipline=discipline, sous=None, epreuve="M.80", chap=chap, difficulte="moyen", type_item="classique", competence="interpréter",
            savoir="Distinguer puissance et énergie consommée", famille="document à lire", titre="L'appareil qui consomme le plus",
            tige=f"L'abonné dont le relevé figure ci-contre veut réduire sa facture et demande à l'agent quel appareil pèse le plus chaque mois, c'est-à-dire lequel consomme le plus d'énergie compte tenu de sa puissance et de sa durée d'usage. Lequel l'agent doit-il désigner ?",
            bonne=gros[0], faux=[a for a, _, _ in apps if a != gros[0]][:3] + ["Tous consomment autant"],
            correction=f"L'énergie est P × t : {', '.join(f'{a} {fmt(p * h / 1000, 2)} kWh/j' for a, p, h in apps)} ; le plus gourmand est {gros[0]} ({fmt(gros[1] * gros[2] / 1000, 2)} kWh/j), pas forcément l'appareil le plus puissant.",
            erreurs=["appareil le plus puissant choisi", "durée seule considérée", "lecture partielle", "égalité supposée"], figure=fig, legende=leg, rnd=rnd)
    budget = rnd.choice([15000, 20000, 25000, 30000, 40000])
    cout = ej * 30 * prix
    ajouter(id_=f"FIG2-EL-fac-{k}-3", discipline=discipline, sous=None, epreuve="M.80", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Coût de l'énergie et respect d'un budget", famille="décision professionnelle", titre="Le budget électricité est-il tenable ?",
            tige=f"La SNEL facture le kWh {prix} FC dans ce quartier. En conservant les appareils et les durées d'usage du relevé ci-contre, l'abonné se fixe un budget d'électricité de {fc(budget)} FC par mois de 30 jours. Que doit-il conclure, et pourquoi ?",
            bonne=(f"Budget tenu, car {fmt(ej * 30, 0)} kWh × {prix} FC ≈ {fc(cout)} FC, sous {fc(budget)} FC" if cout <= budget else f"Budget dépassé, car {fmt(ej * 30, 0)} kWh × {prix} FC ≈ {fc(cout)} FC, au-dessus de {fc(budget)} FC"),
            faux=[(f"Budget dépassé, car {fmt(sum(p for _, p, _ in apps))} W × {prix} FC = {fc(sum(p for _, p, _ in apps) * prix)} FC" if sum(p for _, p, _ in apps) * prix > budget else f"Budget tenu, car {fmt(sum(p for _, p, _ in apps))} W × {prix} FC = {fc(sum(p for _, p, _ in apps) * prix)} FC"),
                  f"Budget tenu, car {fmt(ej, 1)} kWh par jour × {prix} FC = {fc(ej * prix)} FC", f"Budget dépassé, car chaque appareil coûte {prix} FC par heure", f"Impossible de conclure sans la tension du réseau"],
            correction=f"Coût = énergie mensuelle × prix = {fmt(ej * 30, 0)} kWh × {prix} FC ≈ {fc(cout)} FC, {'inférieur' if cout <= budget else 'supérieur'} au budget.",
            erreurs=["puissance facturée au lieu de l'énergie", "coût journalier comparé au budget mensuel", "tarif mal appliqué", "donnée inutile"], figure=fig, legende=leg, rnd=rnd)


# ======================================================================================================================
# MÉCANIQUE APPLIQUÉE / RÉSISTANCE DES MATÉRIAUX
# ======================================================================================================================

def r_poutre(rnd: random.Random, k: int, discipline="Résistance des matériaux"):
    ep = {"Résistance des matériaux": "M.761", "Béton armé": "M.761"}.get(discipline, "M.761")
    L = rnd.choice([4, 5, 6, 8]); a = rnd.choice([v for v in (1, 1.5, 2, 2.5, 3, 4) if v < L]); F = rnd.choice([10, 12, 20, 24, 30, 40])
    b = L - a; RA = F * b / L; RB = F * a / L; Mmax = F * a * b / L
    fig = poutre(L, a, F); leg = f"Poutre sur deux appuis, charge ponctuelle F à {fmt(a)} m de A"
    chap = chapitre(discipline, "poutre", "flexion", "appuis", "statique", "résistance", "effort")
    ctx = rnd.choice(["une passerelle de chantier", "une poutre de hangar", "un pont provisoire sur une rivière", "le portique d'un garage"])
    ajouter(id_=f"FIG2-{'BA' if discipline == 'Béton armé' else 'RM'}-pou-{k}-1", discipline=discipline, sous=None, epreuve=ep, chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Réactions d'appui d'une poutre isostatique (équilibre des moments)", famille="document technique", titre="Réaction à l'appui A",
            tige=f"La figure représente {ctx} : une poutre de {fmt(L)} m sur deux appuis A et B, chargée par une force F = {fmt(F)} kN à {fmt(a)} m de A ; le poids propre est négligé. Quelle est la réaction de l'appui A ?",
            bonne=f"{fmt(RA, 2)} kN", faux=[f"{fmt(RB, 2)} kN" if fmt(RB, 2) != fmt(RA, 2) else f"{fmt(F, 2)} kN", f"{fmt(F / 2, 2)} kN" if fmt(F / 2, 2) not in (fmt(RA, 2), fmt(RB, 2)) else f"{fmt(F, 2)} kN", f"{fmt(F * a / L, 2) if fmt(F * a / L, 2) not in (fmt(RA, 2), fmt(F / 2, 2)) else fmt(F * 2, 2)} kN", f"{fmt(F * L / b, 2)} kN"],
            correction=f"Moments par rapport à B : R_A × {fmt(L)} = F × b = {fmt(F)} × {fmt(b)} ⇒ R_A = {fmt(RA, 2)} kN ; R_B = F − R_A = {fmt(RB, 2)} kN (la réaction la plus forte est du côté de la charge).",
            erreurs=["réaction de B", "charge partagée à parts égales", "bras de levier inversé", "rapport inversé"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-{'BA' if discipline == 'Béton armé' else 'RM'}-pou-{k}-2", discipline=discipline, sous=None, epreuve=ep, chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Moment fléchissant maximal sous une charge ponctuelle : M = F·a·b/L", famille="document technique", titre="Moment fléchissant maximal",
            tige=f"Pour la poutre ci-contre ({fmt(L)} m, F = {fmt(F)} kN à {fmt(a)} m de A), le bureau d'études doit connaître le moment fléchissant maximal, atteint sous la charge. Quelle est sa valeur ?",
            bonne=f"{fmt(Mmax, 2)} kN·m", faux=[f"{fmt(F * L / 4, 2)} kN·m" if fmt(F * L / 4, 2) != fmt(Mmax, 2) else f"{fmt(F * L / 8, 2)} kN·m", f"{fmt(F * a, 2)} kN·m" if fmt(F * a, 2) != fmt(Mmax, 2) else f"{fmt(F * b, 2)} kN·m", f"{fmt(F * L, 2)} kN·m", f"{fmt(RA * L, 2)} kN·m"],
            correction=f"M_max = R_A × a = {fmt(RA, 2)} × {fmt(a)} = F·a·b/L = {fmt(F)}×{fmt(a)}×{fmt(b)}/{fmt(L)} = {fmt(Mmax, 2)} kN·m.",
            erreurs=["formule FL/4 valable seulement à mi-portée", "F × a sans tenir compte de la réaction", "F × L", "R_A × L"], figure=fig, legende=leg, rnd=rnd)
    Madm = rnd.choice([round(Mmax * 0.8, 1), round(Mmax * 1.2, 1), round(Mmax * 1.5, 1), round(Mmax * 0.95, 1)])
    ajouter(id_=f"FIG2-{'BA' if discipline == 'Béton armé' else 'RM'}-pou-{k}-3", discipline=discipline, sous=None, epreuve=ep, chap=chap, difficulte="difficile", type_item="decision", competence="décider",
            savoir="Vérification d'une poutre : moment maximal et moment admissible", famille="décision professionnelle", titre="La poutre peut-elle porter la charge ?",
            tige=f"Le profilé prévu pour {ctx} (figure ci-contre) admet un moment fléchissant de {fmt(Madm, 1)} kN·m au maximum. La charge F = {fmt(F)} kN est appliquée à {fmt(a)} m de A sur {fmt(L)} m de portée. Que doit décider l'ingénieur, et pourquoi ?",
            bonne=(f"Valider le profilé, car M_max = F·a·b/L = {fmt(Mmax, 2)} kN·m reste sous {fmt(Madm, 1)} kN·m" if Mmax <= Madm else f"Renforcer la poutre, car M_max = F·a·b/L = {fmt(Mmax, 2)} kN·m dépasse {fmt(Madm, 1)} kN·m"),
            faux=[(f"Renforcer, car F·L/4 = {fmt(F * L / 4, 2)} kN·m dépasse {fmt(Madm, 1)}" if F * L / 4 > Madm else f"Valider, car F·L/4 = {fmt(F * L / 4, 2)} kN·m reste sous {fmt(Madm, 1)}") if (F * L / 4 > Madm) != (Mmax > Madm) else (f"Renforcer, car F·a = {fmt(F * a, 2)} kN·m dépasse {fmt(Madm, 1)}" if F * a > Madm else f"Valider, car F·a = {fmt(F * a, 2)} kN·m reste sous {fmt(Madm, 1)}"),
                  f"Valider, car la charge {fmt(F)} kN est inférieure à {fmt(Madm, 1)}", f"Renforcer, car les réactions d'appui dépassent toujours le moment admissible", f"Valider, car déplacer la charge au milieu réduirait le moment"],
            correction=f"M_max = {fmt(F)}×{fmt(a)}×{fmt(b)}/{fmt(L)} = {fmt(Mmax, 2)} kN·m, {'inférieur' if Mmax <= Madm else 'supérieur'} à {fmt(Madm, 1)} kN·m. Une force (kN) ne se compare pas à un moment (kN·m) ; FL/4 ne vaut qu'à mi-portée, où le moment serait d'ailleurs maximal.",
            erreurs=["formule à mi-portée ou F·a", "force comparée à un moment", "réactions confondues avec moments", "effet d'un déplacement inversé"], figure=fig, legende=leg, rnd=rnd)


# ======================================================================================================================
# STATISTIQUE (options commerciales et secrétariat)
# ======================================================================================================================

def st_secteurs(rnd: random.Random, k: int, discipline="Statistique"):
    cats = rnd.choice([(["Alimentation", "Loyer", "Transport", "Santé", "Autres"], "dépenses d'un ménage"), (["Manioc", "Maïs", "Riz", "Arachide", "Autres"], "ventes d'une coopérative"),
                       (["Kinshasa", "Katanga", "Kasaï", "Kivu", "Autres"], "clients d'une société"), (["Espèces", "Mobile money", "Chèque", "Virement", "Autres"], "modes de paiement d'un commerce")])
    vals = [rnd.randint(10, 40) for _ in cats[0]]; tot = sum(vals)
    fig = pie(list(zip(cats[0], vals))); leg = f"Répartition des {cats[1]} (secteurs)"
    total_fc = rnd.choice([500000, 800000, 1200000, 2000000])
    imax = vals.index(max(vals))
    chap = chapitre(discipline, "graphique", "représentation", "fréquence")
    ajouter(id_=f"FIG2-ST-sec-{k}-1", discipline=discipline, sous=None, epreuve="M.14", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Lecture d'un diagramme circulaire : fréquence et effectif", famille="document à lire", titre="Montant d'un secteur",
            tige=f"Le diagramme ci-contre représente la répartition des {cats[1]} ; le total vaut {fc(total_fc)} FC. Un comptable doit retrouver le montant correspondant au secteur « {cats[0][imax]} ». Quel est-il ?",
            bonne=f"{fc(round(total_fc * vals[imax] / tot))} FC", faux=[f"{fc(round(total_fc * vals[imax] / 100))} FC", f"{fc(vals[imax])} FC", f"{fc(round(total_fc / len(cats[0])))} FC", f"{fc(round(total_fc * (1 - vals[imax] / tot)))} FC"],
            correction=f"Part de « {cats[0][imax]} » : {vals[imax]}/{tot} ≈ {fmt(100 * vals[imax] / tot, 0)} % ; montant = {fc(total_fc)} × {fmt(vals[imax] / tot, 3)} ≈ {fc(round(total_fc * vals[imax] / tot))} FC.",
            erreurs=["effectif pris pour un pourcentage", "effectif pris pour un montant", "partage égal", "complément"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-ST-sec-{k}-2", discipline=discipline, sous=None, epreuve="M.14", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Angle d'un secteur circulaire : 360° × fréquence", famille="document à lire", titre="Angle d'un secteur",
            tige=f"Pour redessiner à la main le diagramme ci-contre ({cats[1]}), une secrétaire doit calculer l'angle du secteur « {cats[0][imax]} » ({fmt(100 * vals[imax] / tot, 0)} % du total). Quel angle doit-elle tracer, arrondi au degré ?",
            bonne=f"{fmt(round(360 * vals[imax] / tot), 0)}°", faux=[f"{fmt(round(100 * vals[imax] / tot), 0)}°", f"{fmt(round(180 * vals[imax] / tot), 0)}°", f"{fmt(vals[imax], 0)}°", f"{fmt(round(360 / len(cats[0])), 0)}°"],
            correction=f"Angle = 360° × {vals[imax]}/{tot} ≈ {fmt(round(360 * vals[imax] / tot), 0)}°.",
            erreurs=["pourcentage pris pour un angle", "demi-cercle", "effectif pris pour un angle", "partage égal"], figure=fig, legende=leg, rnd=rnd)
    seuil = rnd.choice([25, 30, 35, 40])
    ajouter(id_=f"FIG2-ST-sec-{k}-3", discipline=discipline, sous=None, epreuve="M.14", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Comparer une fréquence à un seuil de gestion", famille="décision professionnelle", titre="Faut-il alerter la direction ?",
            tige=f"La règle de gestion impose une alerte dès qu'un poste dépasse {seuil} % des {cats[1]}. D'après le diagramme ci-contre (total {fc(total_fc)} FC), que doit faire le gestionnaire, et pourquoi ?",
            bonne=(f"Alerter, car « {cats[0][imax]} » représente {fmt(100 * vals[imax] / tot, 0)} %, au-dessus de {seuil} %" if 100 * vals[imax] / tot > seuil else f"Ne pas alerter, car le poste le plus élevé, « {cats[0][imax]} », ne représente que {fmt(100 * vals[imax] / tot, 0)} %, sous {seuil} %"),
            faux=[(f"Ne pas alerter, car {vals[imax]} est inférieur à {seuil}" if vals[imax] < seuil and 100 * vals[imax] / tot > seuil else f"Alerter, car {vals[imax]} dépasse {seuil}") if (vals[imax] > seuil) != (100 * vals[imax] / tot > seuil) else f"Alerter, car l'angle du secteur « {cats[0][imax]} » dépasse {seuil}°",
                  f"Alerter, car la somme des postes dépasse 100 %", f"Ne pas alerter, car aucun poste ne dépasse {fc(total_fc)} FC", f"Alerter, car {len(cats[0])} postes sur {len(cats[0])} dépassent {seuil}/{len(cats[0])} %"],
            correction=f"La fréquence du poste le plus élevé est {vals[imax]}/{tot} ≈ {fmt(100 * vals[imax] / tot, 0)} %, à comparer au seuil {seuil} %.",
            erreurs=["effectif ou angle comparé à un pourcentage", "somme sans sens", "montant total comparé", "raisonnement absurde"], figure=fig, legende=leg, rnd=rnd)


def st_tableau(rnd: random.Random, k: int, discipline="Statistique"):
    classes = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50)]
    eff = [rnd.randint(2, 15) for _ in classes]; N = sum(eff)
    centres = [(a + b) / 2 for a, b in classes]
    moy = sum(c * e for c, e in zip(centres, eff)) / N
    var = sum(e * (c - moy) ** 2 for c, e in zip(centres, eff)) / N; et = math.sqrt(var)
    fig = table(["Classe (minutes)", "[0 ; 10[", "[10 ; 20[", "[20 ; 30[", "[30 ; 40[", "[40 ; 50["], [["Effectif"] + [str(e) for e in eff]], col_w=[130] + [80] * 5, first_col_bold=True)
    leg = "Durée d'attente des clients (série classée)"
    ctx = rnd.choice(["un guichet de banque", "un cabinet dentaire", "une station de bus", "un bureau de poste"])
    chap = chapitre(discipline, "dispersion", "moyenne", "variance")
    ajouter(id_=f"FIG2-ST-tab-{k}-1", discipline=discipline, sous=None, epreuve="M.14", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Moyenne d'une série classée par les centres de classe", famille="donnée brute", titre="Durée moyenne d'attente",
            tige=f"Le tableau ci-contre donne, pour {N} clients d'{ctx}, la durée d'attente par classe. Le responsable doit calculer la durée moyenne d'attente à l'aide des centres de classe. Quelle valeur obtient-il ?",
            bonne=f"{fmt(moy, 1)} min", faux=[f"{fmt(sum(centres) / 5, 1)} min", f"{fmt(moy + 5, 1)} min", f"{fmt(N / 5, 1)} min", f"{fmt(centres[eff.index(max(eff))], 1)} min"],
            correction=f"Σ centre × effectif = {' + '.join(f'{fmt(c)}×{e}' for c, e in zip(centres, eff))} = {fmt(sum(c * e for c, e in zip(centres, eff)))} ; moyenne = {fmt(sum(c * e for c, e in zip(centres, eff)))}/{N} ≈ {fmt(moy, 1)} min.",
            erreurs=["moyenne des centres sans pondération", "bornes supérieures utilisées", "effectif moyen", "classe modale"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-ST-tab-{k}-2", discipline=discipline, sous=None, epreuve="M.14", chap=chap, difficulte="difficile", type_item="classique", competence="calculer",
            savoir="Écart-type d'une série classée", famille="donnée brute", titre="Dispersion des durées d'attente",
            tige=f"Avec le tableau ci-contre ({N} clients d'{ctx}, moyenne ≈ {fmt(moy, 1)} min), le responsable veut mesurer la dispersion des attentes par l'écart-type (centres de classe). Quelle valeur, arrondie au dixième, obtient-il ?",
            bonne=f"{fmt(et, 1)} min", faux=[f"{fmt(var, 1)} min", f"{fmt(et * 2, 1)} min", f"{fmt(50 - 0, 1)} min", f"{fmt(et / 2, 1)} min"],
            correction=f"Variance = Σe(c − x̄)²/N ≈ {fmt(var, 1)} ; écart-type = √{fmt(var, 1)} ≈ {fmt(et, 1)} min.",
            erreurs=["variance donnée pour l'écart-type", "facteur 2", "étendue", "facteur ½"], figure=fig, legende=leg, rnd=rnd)
    seuil = rnd.choice([20, 30]); part = 100 * sum(e for (a, b), e in zip(classes, eff) if a >= seuil) / N
    ajouter(id_=f"FIG2-ST-tab-{k}-3", discipline=discipline, sous=None, epreuve="M.14", chap=chap, difficulte="moyen", type_item="decision", competence="décider",
            savoir="Fréquence cumulée et objectif de qualité de service", famille="décision professionnelle", titre="L'objectif de service est-il atteint ?",
            tige=f"La direction d'{ctx} exige qu'au plus 20 % des clients attendent {seuil} minutes ou plus. D'après le tableau ci-contre ({N} clients), l'objectif est-il atteint, et pourquoi ?",
            bonne=(f"Oui, car {sum(e for (a, b), e in zip(classes, eff) if a >= seuil)} clients sur {N}, soit {fmt(part, 0)} %, attendent {seuil} min ou plus" if part <= 20 else f"Non, car {sum(e for (a, b), e in zip(classes, eff) if a >= seuil)} clients sur {N}, soit {fmt(part, 0)} %, attendent {seuil} min ou plus"),
            faux=[(f"Non, car la moyenne {fmt(moy, 1)} min dépasse {seuil}" if moy > seuil else f"Oui, car la moyenne {fmt(moy, 1)} min est sous {seuil}") if (moy > seuil) != (part > 20) else (f"Oui, car l'écart-type {fmt(et, 1)} min est inférieur à {seuil}"),
                  f"Non, car {len([1 for (a, b) in classes if a >= seuil])} classes sur 5 dépassent {seuil} min", f"Oui, car l'effectif de la classe [{seuil} ; {seuil + 10}[ est de {eff[[a for a, b in classes].index(seuil)]} seulement", f"Impossible de conclure sans les durées exactes"],
            correction=f"Clients à {seuil} min ou plus : classes [{seuil} ; 50[ → {sum(e for (a, b), e in zip(classes, eff) if a >= seuil)} sur {N} = {fmt(part, 0)} %, {'au plus' if part <= 20 else 'plus de'} 20 %. La moyenne ne répond pas à une question de proportion.",
            erreurs=["moyenne ou écart-type au lieu de la proportion", "classes comptées au lieu des effectifs", "une seule classe considérée", "série classée suffisante pourtant"], figure=fig, legende=leg, rnd=rnd)


# ======================================================================================================================
# ORGANISATION DES ENTREPRISES — bilan fonctionnel
# ======================================================================================================================

def o_bilan(rnd: random.Random, k: int, discipline="Organisation des entreprises"):
    immo = rnd.choice([40, 60, 80, 120]); stocks = rnd.choice([10, 15, 20, 30]); creances = rnd.choice([10, 15, 25]); tres = rnd.choice([5, 8, 12, 20])
    cap = rnd.choice([50, 70, 90, 110]); dlt = rnd.choice([10, 20, 30]); dct = immo + stocks + creances + tres - cap - dlt
    if dct < 5:
        dct = 5; cap = immo + stocks + creances + tres - dlt - dct
    fig = table(["Actif", "Millions FC", "Passif", "Millions FC"],
                [["Immobilisations", f"{immo}", "Capitaux propres", f"{cap}"], ["Stocks", f"{stocks}", "Dettes à long terme", f"{dlt}"], ["Créances clients", f"{creances}", "Dettes à court terme", f"{dct}"],
                 ["Trésorerie", f"{tres}", "", ""], ["Total", f"{immo + stocks + creances + tres}", "Total", f"{cap + dlt + dct}"]], col_w=[150, 100, 170, 100], first_col_bold=True)
    leg = "Bilan simplifié au 31 décembre (millions de FC)"
    FR = cap + dlt - immo; BFR = stocks + creances - dct; TN = FR - BFR
    ent = rnd.choice(["une boulangerie industrielle de Kinshasa", "une société de transport fluvial", "une imprimerie de Lubumbashi", "une coopérative de café"])
    chap = chapitre(discipline, "financière", "bilan", "fonds de roulement")
    ajouter(id_=f"FIG2-OE-bil-{k}-1", discipline=discipline, sous=None, epreuve="M.13", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Fonds de roulement = ressources stables − emplois stables", famille="document à lire", titre="Fonds de roulement",
            tige=f"Le bilan simplifié ci-contre (millions de FC) est celui d'{ent} au 31 décembre. Avant une réunion avec ses associés, le gérant doit calculer le fonds de roulement, différence entre les ressources stables (capitaux propres et dettes à long terme) et les immobilisations. Quelle valeur obtient-il ?",
            bonne=f"{fmt(FR)} millions FC", faux=[f"{fmt(cap - immo)} millions FC" if cap - immo != FR else f"{fmt(FR + dct)} millions FC", f"{fmt(BFR)} millions FC" if BFR != FR else f"{fmt(FR * 2)} millions FC", f"{fmt(stocks + creances + tres)} millions FC", f"{fmt(cap + dlt)} millions FC"],
            correction=f"FR = (capitaux propres + dettes à long terme) − immobilisations = ({cap} + {dlt}) − {immo} = {fmt(FR)} millions FC.",
            erreurs=["dettes à long terme oubliées", "besoin en fonds de roulement", "actif circulant", "ressources stables sans soustraire les immobilisations"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-OE-bil-{k}-2", discipline=discipline, sous=None, epreuve="M.13", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Besoin en fonds de roulement = stocks + créances − dettes à court terme", famille="document à lire", titre="Besoin en fonds de roulement",
            tige=f"Toujours d'après le bilan ci-contre ({ent}), le gérant calcule le besoin en fonds de roulement, différence entre l'actif circulant d'exploitation (stocks et créances) et les dettes à court terme. Quelle valeur obtient-il ?",
            bonne=f"{fmt(BFR)} millions FC", faux=[f"{fmt(stocks + creances + tres - dct)} millions FC", f"{fmt(stocks + creances)} millions FC", f"{fmt(FR)} millions FC" if FR != BFR else f"{fmt(BFR + 10)} millions FC", f"{fmt(dct - stocks - creances)} millions FC" if dct - stocks - creances != BFR else f"{fmt(BFR * 3)} millions FC"],
            correction=f"BFR = ({stocks} + {creances}) − {dct} = {fmt(BFR)} millions FC. La trésorerie n'en fait pas partie.",
            erreurs=["trésorerie incluse", "dettes à court terme oubliées", "fonds de roulement", "signe inversé"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-OE-bil-{k}-3", discipline=discipline, sous=None, epreuve="M.13", chap=chap, difficulte="difficile", type_item="decision", competence="décider",
            savoir="Équilibre financier : FR, BFR et trésorerie nette", famille="décision professionnelle", titre="La banque doit-elle s'inquiéter ?",
            tige=f"Un chargé de clientèle examine le bilan ci-contre d'{ent} avant de renouveler un découvert. Il juge l'équilibre financier sain si le fonds de roulement couvre le besoin en fonds de roulement. Que doit-il conclure, et pourquoi ?",
            bonne=(f"Équilibre sain, car FR = {fmt(FR)} couvre BFR = {fmt(BFR)} : trésorerie nette positive de {fmt(TN)} millions FC" if TN >= 0 else f"Équilibre fragile, car FR = {fmt(FR)} ne couvre pas BFR = {fmt(BFR)} : trésorerie nette négative de {fmt(TN)} millions FC"),
            faux=[(f"Équilibre fragile, car les dettes totales {fmt(dlt + dct)} dépassent les capitaux propres {fmt(cap)}" if dlt + dct > cap else f"Équilibre sain, car les capitaux propres {fmt(cap)} dépassent les dettes totales {fmt(dlt + dct)}") if ((dlt + dct > cap) != (TN < 0)) else f"Équilibre sain, car la trésorerie au bilan ({fmt(tres)}) est positive",
                  f"Équilibre sain, car le total de l'actif égale le total du passif", f"Équilibre fragile, car les immobilisations {fmt(immo)} dépassent les stocks {fmt(stocks)}", f"Impossible de conclure sans le compte de résultat"],
            correction=f"FR = {fmt(FR)} ; BFR = {fmt(BFR)} ; trésorerie nette = FR − BFR = {fmt(TN)} millions FC, {'positive : le cycle d exploitation est financé par des ressources stables' if TN >= 0 else 'négative : l entreprise finance son exploitation par des concours bancaires'}. L'égalité actif/passif est toujours vraie et ne dit rien.",
            erreurs=["endettement global ou trésorerie brute pris pour critère", "égalité comptable sans signification", "comparaison sans sens", "donnée inutile réclamée"], figure=fig, legende=leg, rnd=rnd)


# ======================================================================================================================
# MÉCANIQUE APPLIQUÉE — moteurs thermiques : bilan énergétique
# ======================================================================================================================

def m_bilan(rnd: random.Random, k: int, discipline="Mécanique appliquée"):
    Pu = rnd.choice(list(range(20, 165, 5))); rend = rnd.choice([0.25, 0.27, 0.28, 0.30, 0.32, 0.33, 0.35, 0.36, 0.38, 0.40, 0.42])
    Pth = Pu / rend; pertes = Pth - Pu; refroid = round(pertes * rnd.choice([0.45, 0.5, 0.55]), 1); echap = round(pertes - refroid, 1)
    PCI = rnd.choice([42, 43, 44]); conso_kg_h = Pth * 3600 / (PCI * 1000)
    fig = pie([("Utile (arbre)", Pu), ("Refroidissement", refroid), ("Échappement", echap)]); leg = "Répartition de la puissance du carburant (kW) dans un moteur thermique"
    chap = chapitre(discipline, "bilan", "rendement")
    ctx = rnd.choice(["un groupe électrogène d'hôpital", "une pirogue motorisée", "un tracteur agricole", "un camion de transport de minerai", "une pompe d'irrigation"])
    ajouter(id_=f"FIG2-MA-bil-{k}-1", discipline=discipline, sous=None, epreuve="M.74", chap=chap, difficulte="facile", type_item="classique", competence="calculer",
            savoir="Rendement global d'un moteur thermique = puissance utile / puissance thermique fournie", famille="document technique", titre="Rendement d'un moteur",
            tige=f"Le diagramme ci-contre répartit, en kW, la puissance libérée par le carburant dans le moteur d'{ctx} : {fmt(Pu)} kW sont disponibles sur l'arbre, {fmt(refroid)} kW partent au refroidissement et {fmt(echap)} kW à l'échappement. Quel est le rendement global du moteur ?",
            bonne=f"{fmt(100 * rend, 0)} %", faux=[f"{fmt(100 * Pu / pertes, 0)} %", f"{fmt(100 * pertes / Pth, 0)} %", f"{fmt(100 * Pu / refroid, 0)} %", f"{fmt(100 * Pu / (Pu + echap), 0)} %"],
            correction=f"Puissance fournie = {fmt(Pu)} + {fmt(refroid)} + {fmt(echap)} = {fmt(Pth, 1)} kW ; rendement = {fmt(Pu)}/{fmt(Pth, 1)} = {fmt(100 * rend, 0)} %.",
            erreurs=["utile rapportée aux pertes", "part des pertes", "utile rapportée au refroidissement", "échappement seul retranché"], figure=fig, legende=leg, rnd=rnd)
    ajouter(id_=f"FIG2-MA-bil-{k}-2", discipline=discipline, sous=None, epreuve="M.74", chap=chap, difficulte="moyen", type_item="classique", competence="calculer",
            savoir="Consommation horaire de carburant à partir du bilan de puissance et du PCI", famille="document technique", titre="Consommation horaire",
            tige=f"Le carburant du moteur d'{ctx} a un pouvoir calorifique de {PCI} MJ/kg. À partir de la puissance totale fournie par le carburant que révèle le diagramme ci-contre, le mécanicien veut connaître la consommation horaire du moteur à ce régime. Quelle valeur, arrondie au dixième, obtient-il ?",
            bonne=f"{fmt(conso_kg_h, 1)} kg/h", faux=[f"{fmt(Pu * 3600 / (PCI * 1000), 1)} kg/h", f"{fmt(Pth / PCI, 1)} kg/h", f"{fmt(conso_kg_h / 60, 2)} kg/h", f"{fmt(conso_kg_h * 1000, 0)} kg/h"],
            correction=f"Énergie fournie par heure = {fmt(Pth, 1)} kW × 3600 s = {fmt(Pth * 3.6, 0)} MJ ; masse = {fmt(Pth * 3.6, 0)}/{PCI} ≈ {fmt(conso_kg_h, 1)} kg/h.",
            erreurs=["puissance utile au lieu de la puissance fournie", "secondes oubliées", "par minute", "unités mélangées"], figure=fig, legende=leg, rnd=rnd)
    reserve = rnd.choice([20, 30, 40, 50]); duree = rnd.choice([3, 4, 6, 8]); besoin = conso_kg_h * duree / 0.84  # gazole ≈ 0,84 kg/L
    ajouter(id_=f"FIG2-MA-bil-{k}-3", discipline=discipline, sous=None, epreuve="M.74", chap=chap, difficulte="difficile", type_item="decision", competence="décider",
            savoir="Autonomie d'un moteur à partir du bilan énergétique", famille="décision professionnelle", titre="Le réservoir suffira-t-il ?",
            tige=f"Le réservoir d'{ctx} contient {reserve} L de gazole (0,84 kg/L, PCI {PCI} MJ/kg). Le responsable doit garantir {duree} h de fonctionnement continu au régime du diagramme ci-contre avant le prochain ravitaillement. Que doit-il décider, et pourquoi ?",
            bonne=(f"Ne pas ravitailler avant, car {duree} h × {fmt(conso_kg_h, 1)} kg/h ÷ 0,84 ≈ {fmt(besoin, 0)} L, moins que les {reserve} L" if besoin <= reserve else f"Ravitailler avant, car {duree} h × {fmt(conso_kg_h, 1)} kg/h ÷ 0,84 ≈ {fmt(besoin, 0)} L, plus que les {reserve} L"),
            faux=[(f"Ravitailler avant, car {duree} h × {fmt(Pu * 3600 / (PCI * 1000), 1)} kg/h ÷ 0,84 ≈ {fmt(Pu * 3600 / (PCI * 1000) * duree / 0.84, 0)} L dépassent {reserve} L" if Pu * 3600 / (PCI * 1000) * duree / 0.84 > reserve else f"Ne pas ravitailler, car seule la puissance utile {fmt(Pu)} kW consomme du carburant, soit {fmt(Pu * 3600 / (PCI * 1000) * duree / 0.84, 0)} L"),
                  f"Ne pas ravitailler, car {reserve} L × 0,84 = {fmt(reserve * 0.84, 1)} kg dépassent la consommation horaire {fmt(conso_kg_h, 1)} kg/h", f"Ravitailler avant, car les pertes {fmt(pertes, 1)} kW vident le réservoir en moins de {duree} h quelle que soit la réserve", f"Impossible de décider sans la cylindrée du moteur"],
            correction=f"Consommation = {fmt(Pth, 1)} kW × 3600/{PCI * 1000} = {fmt(conso_kg_h, 1)} kg/h ; en {duree} h : {fmt(conso_kg_h * duree, 1)} kg = {fmt(besoin, 0)} L, {'inférieur' if besoin <= reserve else 'supérieur'} à {reserve} L. Toute la puissance fournie (utile et pertes) est tirée du carburant.",
            erreurs=["pertes exclues de la consommation", "réserve comparée à une consommation horaire", "pertes seules considérées", "donnée inutile réclamée"], figure=fig, legende=leg, rnd=rnd)


def b_poutre(rnd, k):
    r_poutre(rnd, k, discipline="Béton armé")


# ======================================================================================================================
def d_pyramide(rnd, k):
    g_pyramide(rnd, k, discipline="Démographie", epreuve="M.56")


def e2_parallele(rnd, k):
    e_parallele(rnd, k, discipline="Électricité générale")


def r2_poutre(rnd, k):
    r_poutre(rnd, k, discipline="Résistance des matériaux")


GABARITS = {
    "Géographie": [g_climato, g_pyramide, g_evolution],
    "Électricité": [e_parallele, e_facture],
    "Mécanique appliquée": [m_bilan],
    "Résistance des matériaux": [r2_poutre],
    "Béton armé": [b_poutre],
    "Statistique": [st_secteurs, st_tableau],
    "Démographie": [d_pyramide],
    "Organisation des entreprises": [o_bilan],
}


def produire(variantes: int, graine: int = 2026) -> list[dict]:
    ITEMS.clear(); SAUTES.clear()
    for disc, gens in GABARITS.items():
        for g in gens:
            for k in range(1, variantes + 1):
                rnd = random.Random(f"{graine}-{g.__name__}-{k}")
                g(rnd, k)
    return list(ITEMS)
