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
        return sql.replace("?", "%s")

    def execute(self, sql: str, params=()):
        sql2 = self._sql(sql)
        lastrowid = None
        if re.match(r"\s*INSERT\s+INTO\s+(lots_generation|resultats|epreuves|quotas|programme)\b", sql, re.I) \
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


def migrer() -> None:
    """Ajoute les colonnes apparues après la V1 sur une base existante."""
    with connect() as con:
        cols = colonnes(con, "items")
        if "situation_id" not in cols:
            con.execute("ALTER TABLE items ADD COLUMN situation_id TEXT REFERENCES situations(id)")
            con.execute("ALTER TABLE items ADD COLUMN ordre_situation INTEGER")


def maintenant() -> str:
    from datetime import datetime
    return datetime.now().isoformat(timespec="seconds")


def preparer(demo_si_vide: bool = True) -> None:
    """Initialise la base, charge le E.32 et, si la banque est vide, les items de démonstration."""
    from .seed import seed

    init_db()
    seed()
    if demo_si_vide:
        with connect() as con:
            n = one(con, "SELECT COUNT(*) n FROM items")["n"]
        if n == 0:
            from .demo import charger_demo, charger_situation_demo
            charger_demo()
            charger_situation_demo()
