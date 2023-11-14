"""SQLite storage for brewd."""

from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS members (
    name   TEXT PRIMARY KEY,
    joined TEXT NOT NULL,
    mug    TEXT NOT NULL DEFAULT 'unknown'
);

CREATE TABLE IF NOT EXISTS rounds (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    maker        TEXT NOT NULL,
    made_at      TEXT NOT NULL,
    biscuit_cost REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS drinkers (
    round_id INTEGER NOT NULL,
    member   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS biscuit_balances (
    member  TEXT PRIMARY KEY,
    balance REAL NOT NULL DEFAULT 0.0
);
"""


def connect(path: str = ":memory:") -> sqlite3.Connection:
    """Open a connection and make sure the schema exists."""
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
