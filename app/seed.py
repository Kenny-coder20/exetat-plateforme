"""Données de configuration : E.32 session 2026, option 1.02 Sciences, et programme indicatif.

Le programme ci-dessous est INDICATIF (cahier des charges § 5 + programme national usuel de 4e des
humanités, section Sciences). Remplacez-le par le programme officiel via `python -m app.cli programme
--fichier programme.csv` (colonnes : discipline, sous_discipline, chapitre, poids).
"""
from .db import connect

OPTIONS = [("1.02", "Sciences", 2026)]

# (jour, code, libellé, nb_items, nb_series, durée h, actif)
EPREUVES = {
    "1.02": [
        (1, "M.01", "Culture générale", 20, 4, 2, 0),
        (2, "M.46", "Mathématiques et SVT", 30, 4, 5, 1),
        (3, "M.07", "SPTIC — Chimie, Physique, TIC", 15, 4, 4, 1),
        (4, "M.36", "Langues", 20, 4, 4, 0),
    ]
}

# (option, jour, ordre, discipline, sous_discipline, nb_items)
QUOTAS = [
    ("1.02", 1, 1, "Civisme", None, 2),
    ("1.02", 1, 2, "Géographie", None, 6),
    ("1.02", 1, 3, "Histoire", None, 6),
    ("1.02", 1, 4, "Philosophie", None, 6),
    ("1.02", 2, 1, "Mathématiques", None, 15),
    ("1.02", 2, 2, "SVT", "Biologie", 7),
    ("1.02", 2, 3, "SVT", "Écologie", 5),
    ("1.02", 2, 4, "SVT", "Géologie & Évolution", 3),
    ("1.02", 3, 1, "Chimie", None, 6),
    ("1.02", 3, 2, "Physique", None, 6),
    ("1.02", 3, 3, "TIC", None, 3),
    ("1.02", 4, 1, "Anglais", None, 9),
    ("1.02", 4, 2, "Français", None, 11),
]

# (discipline, sous_discipline, chapitre, poids)
PROGRAMME = [
    ("Mathématiques", None, "Nombres complexes", 2),
    ("Mathématiques", None, "Exponentielles et logarithmes", 2),
    ("Mathématiques", None, "Développements de Maclaurin", 1),
    ("Mathématiques", None, "Différentielles et dérivées", 2),
    ("Mathématiques", None, "Primitives et intégrales", 2),
    ("Mathématiques", None, "Probabilités", 2),
    ("Mathématiques", None, "Coniques", 1),
    ("Mathématiques", None, "Géométrie plane", 1),
    ("Mathématiques", None, "Géométrie dans l'espace", 1),
    ("Mathématiques", None, "Statistiques", 1),
    ("SVT", "Biologie", "Reproduction humaine et hormones", 2),
    ("SVT", "Biologie", "Génétique et hérédité", 2),
    ("SVT", "Biologie", "Immunologie et groupes sanguins", 1),
    ("SVT", "Biologie", "Système nerveux", 1),
    ("SVT", "Biologie", "Nutrition et santé", 1),
    ("SVT", "Écologie", "Écosystèmes et chaînes alimentaires", 2),
    ("SVT", "Écologie", "Cycles biogéochimiques", 1),
    ("SVT", "Écologie", "Protection de la nature et pollution", 2),
    ("SVT", "Géologie & Évolution", "Structure de la Terre et roches", 1),
    ("SVT", "Géologie & Évolution", "Évolution des espèces", 1),
    ("SVT", "Géologie & Évolution", "Fossiles et temps géologiques", 1),
    ("Chimie", None, "Stœchiométrie et quantité de matière", 2),
    ("Chimie", None, "Solutions et concentrations", 1),
    ("Chimie", None, "Acides, bases et pH", 1),
    ("Chimie", None, "Oxydoréduction", 1),
    ("Chimie", None, "Chimie organique : hydrocarbures et fonctions", 1),
    ("Physique", None, "Électricité : loi d'Ohm, puissance, énergie", 2),
    ("Physique", None, "Mécanique : forces, mouvement, travail", 1),
    ("Physique", None, "Optique géométrique", 1),
    ("Physique", None, "Électromagnétisme et courant alternatif", 1),
    ("Physique", None, "Ondes et son", 1),
    ("TIC", None, "Tableur : formules et graphiques", 1),
    ("TIC", None, "Traitement de texte et fichiers", 1),
    ("TIC", None, "Réseaux, Internet et sécurité numérique", 1),
]


def seed(replace_programme: bool = False) -> None:
    with connect() as con:
        for code, nom, session in OPTIONS:
            con.execute(
                "INSERT INTO options(code, nom, session) VALUES(?,?,?) "
                "ON CONFLICT(code) DO UPDATE SET nom=excluded.nom, session=excluded.session",
                (code, nom, session),
            )
        for opt, eps in EPREUVES.items():
            for jour, code, lib, nb, ns, h, actif in eps:
                con.execute(
                    "INSERT INTO epreuves(option_code, jour, code, libelle, nb_items, nb_series, duree_h, actif) "
                    "VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(option_code, jour) DO UPDATE SET code=excluded.code, "
                    "libelle=excluded.libelle, nb_items=excluded.nb_items, nb_series=excluded.nb_series, "
                    "duree_h=excluded.duree_h, actif=excluded.actif",
                    (opt, jour, code, lib, nb, ns, h, actif),
                )
        con.execute("DELETE FROM quotas")
        for opt, jour, ordre, disc, sous, nb in QUOTAS:
            ep = con.execute("SELECT id FROM epreuves WHERE option_code=? AND jour=?", (opt, jour)).fetchone()
            con.execute(
                "INSERT INTO quotas(epreuve_id, ordre, discipline, sous_discipline, nb_items) VALUES(?,?,?,?,?)",
                (ep["id"], ordre, disc, sous, nb),
            )
        n = con.execute("SELECT COUNT(*) AS n FROM programme").fetchone()["n"]
        if n == 0 or replace_programme:
            con.execute("DELETE FROM programme")
            con.executemany(
                "INSERT INTO programme(discipline, sous_discipline, chapitre, poids, source) VALUES(?,?,?,?,'indicatif')",
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
