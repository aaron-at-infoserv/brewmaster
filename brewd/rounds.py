"""Recording rounds and working out whose turn it is."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from brewd import ledger
from brewd.members import member_names


def record_round(
    conn: sqlite3.Connection,
    maker: str,
    drinkers: list[str] | None = None,
    biscuit_cost: float = 0.0,
    made_at: str | None = None,
) -> int:
    """Record a round of tea. Returns the new round id.

    If no drinker list is given, the whole team is assumed to have had one.
    """
    if drinkers is None:
        drinkers = member_names(conn)
    if made_at is None:
        made_at = datetime.now(UTC).isoformat(timespec="seconds")

    cur = conn.execute(
        "INSERT INTO rounds (maker, made_at, biscuit_cost) VALUES (?, ?, ?)",
        (maker, made_at, biscuit_cost),
    )
    round_id = int(cur.lastrowid)
    for drinker in drinkers:
        conn.execute(
            "INSERT INTO drinkers (round_id, member) VALUES (?, ?)",
            (round_id, drinker),
        )
    conn.commit()

    if biscuit_cost:
        ledger.charge_biscuits(conn, maker, drinkers, biscuit_cost)

    return round_id


def round_history(conn: sqlite3.Connection, limit: int = 20) -> list[dict]:
    rows = conn.execute(
        "SELECT id, maker, made_at, biscuit_cost FROM rounds "
        "ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def next_brewer(conn: sqlite3.Connection, last_maker: str | None = None) -> str:
    """Work out who should make the next round.

    The team is ordered by how much tea they owe, most first. We then walk
    down that order skipping anyone who cannot take the round: the person who
    made the last one (nobody brews twice running), and anyone already
    carrying their fair share or less.
    """
    debts = ledger.all_debts(conn)
    if not debts:
        raise ValueError("nobody on the register")

    order = sorted(debts, key=lambda name: (-debts[name], name))
    if not conn.execute("SELECT 1 FROM rounds LIMIT 1").fetchone():
        # Nobody has made a round yet, so just start at the top of the list.
        return order[0]

    fair_share = ledger.average_debt(conn)
    idx = 0
    while order[idx] == last_maker or debts[order[idx]] <= fair_share:
        idx = (idx + 1) % len(order)
    return order[idx]


def start_new_quarter(conn: sqlite3.Connection) -> None:
    """Clear the board down for a new quarter.

    Last quarter's rounds do not carry over. Everyone starts level: the history
    is wiped and each member is credited with one round for the team, so nobody
    begins the quarter already in credit.
    """
    conn.execute("DELETE FROM drinkers")
    conn.execute("DELETE FROM rounds")
    conn.commit()
    for name in member_names(conn):
        record_round(conn, maker=name)
