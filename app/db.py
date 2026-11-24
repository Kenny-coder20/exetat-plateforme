"""Accès base de données : SQLite en local, PostgreSQL quand DATABASE_URL est défini (Render).

Le reste du code écrit du SQL avec des « ? » et appelle .execute().fetchone()/.fetchall()/.lastrowid :
le petit wrapper ci-dessous rend ces appels identiques sur les deux moteurs.
"""
from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
PG = DATABASE_URL.startswith(("postgres://", "postgresql://"))
DB_PATH = Path(os.environ.get("EXETAT_DB", ROOT / "data" / "exetat.sqlite"))
SCHEMA_SQLITE = Path(__file__).with_name("schema.sql")
SCHEMA_PG = Path(__file__).with_name("schema_pg.sql")


class _Cursor:
    def __init__(self, cur, lastrowid=None):
        self._cur = cur
        self.lastrowid = lastrowid

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def __iter__(self):
        return iter(self._cur.fetchall())


class _PgConn:
    """Connexion psycopg qui parle comme sqlite3 (placeholders « ? », lastrowid, dict rows)."""

    def __init__(self, con):
        self._con = con

    @staticmethod
    def _sql(sql: str) -> str:
        # un % littéral (LIKE 'abc%') doit être doublé pour psycopg ; les « ? » deviennent %s
        return sql.replace("%", "%%").replace("?", "%s")

    def execute(self, sql: str, params=()):
        sql2 = self._sql(sql)
        lastrowid = None
        if re.match(r"\s*INSERT\s+INTO\s+(lots_generation|resultats|quotas|programme|corrections|relectures)\b", sql, re.I) \
                and "RETURNING" not in sql.upper():
            sql2 += " RETURNING id"
            cur = self._con.execute(sql2, params)
            row = cur.fetchone()
            lastrowid = row["id"] if row else None
            return _Cursor(cur, lastrowid)
        return _Cursor(self._con.execute(sql2, params))

    def executemany(self, sql: str, seq):
        with self._con.cursor() as cur:
            cur.executemany(self._sql(sql), list(seq))

    def executescript(self, script: str):
        self._con.execute(script)

    def commit(self):
        self._con.commit()

    def close(self):
        self._con.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self._con.commit()
        else:
            self._con.rollback()
        self._con.close()


def connect():
    if PG:
        import psycopg
        from psycopg.rows import dict_row

        return _PgConn(psycopg.connect(DATABASE_URL, row_factory=dict_row))
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db() -> None:
    _migrer_avant()
    with connect() as con:
        con.executescript((SCHEMA_PG if PG else SCHEMA_SQLITE).read_text(encoding="utf-8"))
    migrer()


def rows(con, sql, params=()):
    return [dict(r) for r in con.execute(sql, params).fetchall()]


def one(con, sql, params=()):
    r = con.execute(sql, params).fetchone()
    return dict(r) if r else None


def colonnes(con, table: str) -> set[str]:
    if PG:
        return {r["column_name"] for r in con.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name=?", (table,)).fetchall()}
    return {r["name"] for r in con.execute(f"PRAGMA table_info({table})").fetchall()}


EPREUVE_PAR_DISCIPLINE_V1 = {  # pour rattacher les items de la V1 (option Sciences) à leur épreuve
    "Mathématiques": "M.46", "SVT": "M.46", "Chimie": "M.07", "Physique": "M.07", "TIC": "M.07",
    "Civisme": "M.01", "Géographie": "M.01", "Histoire": "M.01", "Philosophie": "M.01",
}


def _migrer_avant() -> None:
    """V2 → V3 : les épreuves deviennent partagées et identifiées par leur code ; les anciennes tables de
    configuration (recréées à partir du E.32 à chaque démarrage) sont supprimées avant la création du schéma."""
    with connect() as con:
        if "jour" in colonnes(con, "epreuves"):
            con.execute("DROP TABLE IF EXISTS quotas")
            con.execute("DROP TABLE IF EXISTS epreuves")


def migrer() -> None:
    """Fait évoluer une base existante vers le schéma courant sans perdre les items."""
    with connect() as con:
        cols = colonnes(con, "items")
        if "situation_id" not in cols:
            con.execute("ALTER TABLE items ADD COLUMN situation_id TEXT REFERENCES situations(id)")
            con.execute("ALTER TABLE items ADD COLUMN ordre_situation INTEGER")
        if "famille" not in colonnes(con, "options"):
            con.execute("ALTER TABLE options ADD COLUMN famille TEXT")
        if "epreuve_code" not in colonnes(con, "programme"):
            con.execute("ALTER TABLE programme ADD COLUMN epreuve_code TEXT")
        if "epreuve_code" not in colonnes(con, "situations"):
            con.execute("ALTER TABLE situations ADD COLUMN epreuve_code TEXT")
        if "epreuve_code" not in colonnes(con, "resultats"):
            con.execute("ALTER TABLE resultats ADD COLUMN epreuve_code TEXT")
    with connect() as con:
        for disc, code in EPREUVE_PAR_DISCIPLINE_V1.items():
            con.execute("UPDATE items SET epreuve_code=? WHERE epreuve_code IS NULL AND discipline=?", (code, disc))
            con.execute("UPDATE situations SET epreuve_code=? WHERE epreuve_code IS NULL AND discipline=?", (code, disc))


def maintenant() -> str:
    from datetime import datetime
    return datetime.now().isoformat(timespec="seconds")


def preparer(demo_si_vide: bool = True) -> None:
    """Initialise la base, charge le E.32 et, si la banque est vide, les items de démonstration."""
    from .seed import seed

    init_db()
    seed()
    from .auth import amorcer
    amorcer()
    if demo_si_vide:
        with connect() as con:
            n = one(con, "SELECT COUNT(*) n FROM items")["n"]
        if n == 0:
            from .demo import charger_demo, charger_situation_demo
            charger_demo()
            charger_situation_demo()
