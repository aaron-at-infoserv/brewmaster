import pytest

from brewd import ledger
from brewd.rounds import next_brewer, record_round, round_history


def test_a_round_is_recorded(db):
    round_id = record_round(db, "alice", drinkers=["alice", "bob"])
    assert round_id == 1
    history = round_history(db)
    assert len(history) == 1
    assert history[0]["maker"] == "alice"


def test_history_is_newest_first(db):
    record_round(db, "alice", drinkers=["alice", "bob"])
    record_round(db, "bob", drinkers=["alice", "bob"])
    assert [r["maker"] for r in round_history(db)] == ["bob", "alice"]


def test_next_brewer_is_whoever_owes_most(db):
    # Setup: alice made 0 rounds, received 0
    # bob made 0 rounds, received 1 (from alice's first round)
    # carol made 0 rounds, received 1 (from alice's first round)
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    assert ledger.debt(db, "bob") == 1
    assert next_brewer(db) == "bob"


def test_nobody_brews_twice_running(db):
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    assert next_brewer(db, last_maker="bob") == "carol"


def test_inactive_members_not_selected(db):
    # Setup: dave has highest debt but is inactive
    record_round(db, "dave", drinkers=["dave", "alice", "bob"])
    record_round(db, "alice", drinkers=["alice", "bob"])

    # Dave's debt is 1 (received 1, made 1) but inactive
    # Bob's debt is 2 (received 2, made 1)
    # Alice's debt is 1 (received 2, made 1)
    from brewd.api import deactivate_member
    deactivate_member(db, "dave")

    # Should select Bob, not Dave
    assert next_brewer(db) == "bob"


def test_inactive_members_remain_in_status(db):
    record_round(db, "dave", drinkers=["dave", "alice"])
    from brewd.api import status
    status_data = status()
    dave_debt = next(m["owes_rounds"] for m in status_data["members"] if m["name"] == "dave")
    assert dave_debt == 1