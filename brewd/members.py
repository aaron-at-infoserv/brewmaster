"""The team register."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Member:
    name: str
    joined: str
    mug: str


def add_member(
    conn: sqlite3.Connection, name: str, joined: str, mug: str = "unknown"
) -> Member:
    conn.execute(
        "INSERT OR REPLACE INTO members (name, joined, mug) VALUES (?, ?, ?)",
        (name, joined, mug),
    )
    conn.execute(
        "INSERT OR IGNORE INTO biscuit_balances (member, balance) VALUES (?, 0.0)",
        (name,),
    )
    conn.commit()
    return Member(name, joined, mug)


def get_member(conn: sqlite3.Connection, name: str) -> Member | None:
    row = conn.execute("SELECT * FROM members WHERE name = ?", (name,)).fetchone()
    if row is None:
        return None
    return Member(row["name"], row["joined"], row["mug"])


def all_members(conn: sqlite3.Connection) -> list[Member]:
    """Everyone on the register, oldest hand first."""
    rows = conn.execute("SELECT * FROM members ORDER BY joined, name").fetchall()
    return [Member(r["name"], r["joined"], r["mug"]) for r in rows]


def member_names(conn: sqlite3.Connection) -> list[str]:
    return [m.name for m in all_members(conn)]


def purge_member(conn: sqlite3.Connection, name: str) -> bool:
    """Remove someone who has left the team.

    Takes them off the register and clears them out of the rota so they stop
    being nominated. Returns False if they were not on the register.
    """
    if get_member(conn, name) is None:
        return False
    conn.execute(
        "DELETE FROM drinkers WHERE round_id IN "
        "(SELECT id FROM rounds WHERE maker = ?)",
        (name,),
    )
    conn.execute("DELETE FROM rounds WHERE maker = ?", (name,))
    conn.execute("DELETE FROM drinkers WHERE member = ?", (name,))
    conn.execute("DELETE FROM biscuit_balances WHERE member = ?", (name,))
    conn.execute("DELETE FROM members WHERE name = ?", (name,))
    conn.commit()
    return True
