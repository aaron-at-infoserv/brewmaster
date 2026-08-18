import pytest
from brewd.members import add_member, get_member, deactivate_member
from brewd import store


def test_deactivation_sets_inactive_flag(db):
    add_member(db, "dave", "2021-01-01", is_active=True)
    deactivate_member(db, "dave")
    member = get_member(db, "dave")
    assert member.is_active is False


def test_deactivation_preserves_history(db):
    add_member(db, "dave", "2021-01-01", is_active=True)
    # Record some rounds for dave
    from brewd.rounds import record_round
    record_round(db, "dave", drinkers=["dave", "alice"])
    record_round(db, "alice", drinkers=["dave", "alice"])

    deactivate_member(db, "dave")
    history = record_round(db, "bob", drinkers=["bob", "alice"])

    # Dave's rounds should still exist in history
    rounds = store.round_history(db)
    assert any(r["maker"] == "dave" for r in rounds)


def test_inactive_members_remain_in_status(db):
    add_member(db, "dave", "2021-01-01", is_active=True)
    from brewd.rounds import record_round
    record_round(db, "dave", drinkers=["dave", "alice"])

    deactivate_member(db, "dave")
    from brewd.api import status
    status_data = status()
    dave_debt = next(m["owes_rounds"] for m in status_data["members"] if m["name"] == "dave")
    assert dave_debt == 1