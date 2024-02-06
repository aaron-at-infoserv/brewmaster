import pytest

from brewd import ledger
from brewd.rounds import record_round


def test_maker_works_off_their_debt(db):
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    assert ledger.debt(db, "alice") == 0
    assert ledger.debt(db, "bob") == 1
    assert ledger.debt(db, "carol") == 1


def test_debt_accumulates_over_rounds(db):
    for _ in range(3):
        record_round(db, "alice", drinkers=["alice", "bob"])
    assert ledger.brews_made(db, "alice") == 3
    assert ledger.brews_received(db, "bob") == 3
    assert ledger.debt(db, "bob") == 3


def test_fair_share_is_the_mean(db):
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    assert ledger.average_debt(db) == 2 / 3


def test_biscuits_are_split_between_drinkers(db):
    record_round(db, "alice", drinkers=["alice", "bob", "carol"], biscuit_cost=0.60)
    assert ledger.biscuit_balance(db, "bob") == -0.20
    assert ledger.biscuit_balance(db, "carol") == -0.20
    # the maker fronted the money, so they are up by the full packet
    assert ledger.biscuit_balance(db, "alice") == pytest.approx(0.40)


def test_settle_clears_what_is_owed(db):
    record_round(db, "alice", drinkers=["alice", "bob"], biscuit_cost=1.00)
    assert ledger.biscuit_balance(db, "bob") == -0.50
    moved = ledger.settle(db, "bob", "alice")
    assert moved == 0.50
    assert ledger.biscuit_balance(db, "bob") == 0.0
