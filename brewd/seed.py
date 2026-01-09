"""Load a plausible-looking history so the service has something to say.

Run with:  python -m brewd.seed brewmaster.db
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import date, timedelta

from brewd import store
from brewd.members import add_member
from brewd.rounds import record_round

TEAM = [
    ("alice", "2019-04-01", "the big blue one"),
    ("dave", "2021-01-11", "World's Okayest Dad"),
    ("bob", "2022-06-13", "chipped Sports Direct"),
    ("carol", "2023-02-27", "keep cup, allegedly"),
    ("erin", "2024-09-02", "borrowed, never returned"),
    ("frank", "2025-03-17", "a pint glass"),
]

# Who has actually been pulling their weight, in rounds made.
MAKER_SHARE = {
    "alice": 4,
    "bob": 6,
    "carol": 8,
    "erin": 10,
    "frank": 12,
    # dave: none. He has not made a round in a very long time.
}

BISCUIT_COSTS = [0.0, 0.85, 0.0, 1.29, 0.99, 0.0, 1.15, 0.0, 0.79, 1.45]


def seed(conn: sqlite3.Connection) -> None:
    for name, joined, mug in TEAM:
        add_member(conn, name, joined, mug)

    schedule: list[str] = []
    for maker, count in MAKER_SHARE.items():
        schedule.extend([maker] * count)
    schedule.sort(key=lambda n: (MAKER_SHARE[n], n))

    day = date(2026, 1, 5)
    for i, maker in enumerate(schedule):
        record_round(
            conn,
            maker=maker,
            biscuit_cost=BISCUIT_COSTS[i % len(BISCUIT_COSTS)],
            made_at=(day + timedelta(days=i * 2)).isoformat(),
        )


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "brewmaster.db"
    conn = store.connect(path)
    seed(conn)
    print(f"seeded {path}")


if __name__ == "__main__":
    main()
