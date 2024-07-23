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
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    assert ledger.debt(db, "bob") == 1
    assert next_brewer(db) == "bob"


def test_nobody_brews_twice_running(db):
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    assert next_brewer(db, last_maker="bob") == "carol"


def test_empty_register_is_an_error():
    from brewd import store

    with pytest.raises(ValueError):
        next_brewer(store.connect())
