'''The team register.'''

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Member:
    name: str
    joined: str
    mug: str
    is_active: bool


def add_member(
    conn: sqlite3.Connection, name: str, joined: str, mug: str = "unknown", is_active: bool = True
) -> Member:
    conn.execute(
        "INSERT OR REPLACE INTO members (name, joined, mug, is_active) VALUES (?, ?, ?, ?)",
        (name, joined, mug, is_active),
    )
    conn.execute(
        "INSERT OR IGNORE INTO biscuit_balances (member, balance) VALUES (?, 0.0)",
        (name,),
    )
    conn.commit()
    return Member(name, joined, mug, is_active)


def get_member(conn: sqlite3.Connection, name: str) -> Member | None:
    row = conn.execute("SELECT * FROM members WHERE name = ?", (name,)).fetchone()
    if row is None:
        return None
    return Member(row["name"], row["joined"], row["mug"], row["is_active"] == 1)


def all_members(conn: sqlite3.Connection, active_only: bool = False) -> list[Member]:
    query = "SELECT * FROM members"
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY joined, name"
    rows = conn.execute(query).fetchall()
    return [Member(r["name"], r["joined"], r["mug"], r["is_active"] == 1) for r in rows]


def member_names(conn: sqlite3.Connection, active_only: bool = False) -> list[str]:
    return [m.name for m in all_members(conn, active_only=active_only)]