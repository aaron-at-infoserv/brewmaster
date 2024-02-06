"""Fairness accounting.

Two separate books are kept:

* the *brew ledger*, counted in rounds made and rounds received
* the *biscuit ledger*, counted in money
"""

from __future__ import annotations

import sqlite3


def brews_made(conn: sqlite3.Connection, name: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM rounds WHERE maker = ?", (name,)
    ).fetchone()
    return int(row["n"])


def brews_received(conn: sqlite3.Connection, name: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM drinkers WHERE member = ?", (name,)
    ).fetchone()
    return int(row["n"])


def debt(conn: sqlite3.Connection, name: str) -> int:
    """How many rounds this member owes the team.

    Positive means they are in the red and should be making tea.
    """
    return brews_received(conn, name) - brews_made(conn, name)


def all_debts(conn: sqlite3.Connection) -> dict[str, int]:
    from brewd.members import member_names

    return {name: debt(conn, name) for name in member_names(conn)}


def average_debt(conn: sqlite3.Connection) -> float:
    """The fair share. Anyone above this is coasting."""
    debts = all_debts(conn)
    if not debts:
        return 0.0
    return sum(debts.values()) / len(debts)


def biscuit_balance(conn: sqlite3.Connection, name: str) -> float:
    row = conn.execute(
        "SELECT balance FROM biscuit_balances WHERE member = ?", (name,)
    ).fetchone()
    return float(row["balance"]) if row else 0.0


def all_biscuit_balances(conn: sqlite3.Connection) -> dict[str, float]:
    rows = conn.execute("SELECT member, balance FROM biscuit_balances").fetchall()
    return {r["member"]: float(r["balance"]) for r in rows}


def _adjust(conn: sqlite3.Connection, name: str, amount: float) -> None:
    conn.execute(
        "INSERT INTO biscuit_balances (member, balance) VALUES (?, ?) "
        "ON CONFLICT(member) DO UPDATE SET balance = balance + ?",
        (name, amount, amount),
    )


def charge_biscuits(
    conn: sqlite3.Connection, maker: str, drinkers: list[str], cost: float
) -> None:
    """Split the cost of a packet of biscuits across everyone who had one.

    The maker fronts the money and is credited the full amount; every drinker
    is charged an equal share, rounded to the nearest penny.
    """
    if cost <= 0 or not drinkers:
        return
    share = round(cost / len(drinkers), 2)
    for drinker in drinkers:
        _adjust(conn, drinker, -share)
    _adjust(conn, maker, cost)
    conn.commit()


def settle(conn: sqlite3.Connection, payer: str, payee: str) -> float:
    """Settle up between two members.

    Moves whatever the payer owes across to the payee and records a
    compensating brew round so that the brew ledger is left unaffected by
    the settlement. Returns the amount moved.
    """
    owed = -biscuit_balance(conn, payer)
    if owed <= 0:
        return 0.0
    _adjust(conn, payer, owed)
    _adjust(conn, payee, -owed)
    conn.commit()
    return owed
