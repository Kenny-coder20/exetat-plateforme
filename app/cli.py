"""Ligne de commande : python -m app.cli <commande> [options]"""
import argparse
import json
import sys

from . import assemblage, export, generation, seed
from .db import connect, init_db, rows


def cmd_init(a):
    init_db()
    seed.seed(replace_programme=a.reset_programme)
    print("Base initialisée :", end=" ")
    with connect() as con:
        print(f"{len(rows(con, 'SELECT * FROM epreuves'))} épreuves, {len(rows(con, 'SELECT * FROM quotas'))} quotas, "
              f"{len(rows(con, 'SELECT * FROM programme'))} chapitres au programme.")


def cmd_programme(a):
    n = seed.import_programme(a.fichier)
    print(f"Programme remplacé : {n} chapitres importés.")


def cmd_generer(a):
    if a.jour:
        res = generation.generer_epreuve(a.jour, a.serie)
        for r in res:
            q = r["quota"]
            print(f"- {q['discipline']}{' / ' + q['sous_discipline'] if q['sous_discipline'] else ''} : "
                  f"{len(r['ids'])}/{q['nb_items']} items, tokens {r['usage']}, anomalies {r['anomalies_serie']}")
    elif a.situation:
        from . import situations
        r = situations.generer_situation(discipline=a.discipline, sous_discipline=a.sous_discipline,
                                         chapitre=a.chapitre, n=a.n if a.n != 5 else 5)
        print(f"Situation {r['situation_id']} : {r['nb_questions']} questions, tokens {r['usage']}")
        r = {"ids": [], "lot": r["lot"], "usage": r["usage"], "anomalies_serie": []}
    else:
        r = generation.generer(discipline=a.discipline, sous_discipline=a.sous_discipline, n=a.n,
                               chapitre=a.chapitre, difficulte=a.difficulte)
        print(f"{len(r['ids'])} items générés (lot {r['lot']}), tokens {r['usage']}, anomalies {r['anomalies_serie']}")
    print("Les items sont en attente de validation : ouvrez http://127.0.0.1:8000/validateur/")


def cmd_assembler(a):
    if a.jour and not a.discipline:
        s = assemblage.assembler_epreuve(a.jour, graine=a.graine)
        nom = f"J{a.jour}_{s['epreuve']['code'].replace('.', '')}_serie{a.serie}"
        titre = s["epreuve"]["libelle"]
        duree = f"{s['epreuve']['duree_h']:g} h"
        code = s["epreuve"]["code"]
    elif a.jour and a.discipline:
        s = assemblage.assembler_discipline(a.jour, a.discipline, graine=a.graine)
        nom = f"J{a.jour}_{export.nom_fichier(a.discipline)}_serie{a.serie}"
        titre, duree, code = a.discipline, "", s["epreuve"]["code"]
    else:
        s = assemblage.assembler_chapitre(a.discipline, a.chapitre, a.n, a.difficulte, graine=a.graine)
        nom = f"{export.nom_fichier(a.discipline)}_{export.nom_fichier(a.chapitre)}"
        titre, duree, code = f"{a.discipline} — {a.chapitre}", "", "entraînement"
    if s["manques"]:
        print("Banque insuffisante :", s["manques"])
    pj = export.exporter_json(s, nom)
    pt = export.exporter_latex(s, nom, titre_epreuve=titre, code_epreuve=code, serie_lettre=a.serie, duree=duree)
    print(f"{len(s['items'])} items → {pj}\n{pt}")
    if a.pdf:
        pdf = export.compiler_pdf(pt)
        print(pdf if pdf else "pdflatex introuvable : compilez le .tex avec votre distribution LaTeX.")


def cmd_banque(a):
    b = assemblage.banque_validee()
    p = export.EXPORTS / "banque.json"
    export.EXPORTS.mkdir(exist_ok=True)
    p.write_text(json.dumps(b, ensure_ascii=False), encoding="utf-8")
    print(f"Banque exportée : {b['nb_items']} items validés → {p}")


def cmd_stats(a):
    with connect() as con:
        for r in rows(con, "SELECT discipline, COALESCE(sous_discipline,'') sd, statut_validation s, COUNT(*) n "
                           "FROM items GROUP BY 1,2,3 ORDER BY 1,2,3"):
            print(f"{r['discipline']:<15} {r['sd']:<22} {r['s']:<11} {r['n']}")


def cmd_demo(a):
    from .demo import charger_demo, charger_situation_demo
    n = charger_demo()
    sid = charger_situation_demo()
    print(f"{n} items de démonstration et 1 situation étendue ({sid}) insérés et validés (marqués 'demo').")


def main(argv=None):
    p = argparse.ArgumentParser(prog="exetat", description="Plateforme de génération d'items EXETAT")
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("init", help="créer la base et charger le E.32"); s.add_argument("--reset-programme", action="store_true"); s.set_defaults(f=cmd_init)
    s = sp.add_parser("programme", help="importer le programme officiel (CSV)"); s.add_argument("fichier"); s.set_defaults(f=cmd_programme)
    s = sp.add_parser("generer", help="générer des items via l'assistant IA")
    s.add_argument("--jour", type=int); s.add_argument("--serie", default=None)
    s.add_argument("--discipline"); s.add_argument("--sous-discipline"); s.add_argument("--chapitre")
    s.add_argument("--difficulte", choices=["facile", "moyen", "difficile"]); s.add_argument("-n", type=int, default=5)
    s.add_argument("--situation", action="store_true", help="situation étendue : une situation longue + n questions liées")
    s.set_defaults(f=cmd_generer)
    s = sp.add_parser("assembler", help="assembler une série depuis la banque validée")
    s.add_argument("--jour", type=int); s.add_argument("--discipline"); s.add_argument("--chapitre")
    s.add_argument("--difficulte"); s.add_argument("-n", type=int, default=10); s.add_argument("--serie", default="A")
    s.add_argument("--graine", type=int); s.add_argument("--pdf", action="store_true"); s.set_defaults(f=cmd_assembler)
    s = sp.add_parser("banque", help="exporter la banque validée (fichier de l'app élève)"); s.set_defaults(f=cmd_banque)
    s = sp.add_parser("stats", help="état de la banque"); s.set_defaults(f=cmd_stats)
    s = sp.add_parser("demo", help="charger des items de démonstration"); s.set_defaults(f=cmd_demo)
    a = p.parse_args(argv)
    try:
        a.f(a)
    except generation.GenerationError as e:
        print("Erreur :", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
