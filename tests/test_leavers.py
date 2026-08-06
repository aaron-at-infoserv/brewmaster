from brewd import ledger
from brewd.members import member_names, purge_member
from brewd.rounds import next_brewer, record_round


def test_leaver_comes_off_the_register(db):
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    assert purge_member(db, "carol") is True
    assert member_names(db) == ["alice", "bob"]


def test_leaver_is_no_longer_nominated(db):
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    assert ledger.debt(db, "carol") == 1
    purge_member(db, "carol")
    assert "carol" not in ledger.all_debts(db)
    assert next_brewer(db) == "bob"


def test_purging_someone_who_was_never_here(db):
    assert purge_member(db, "marcus") is False


def test_endpoint_removes_a_leaver(client):
    client.post("/members", json={"name": "gita", "joined": "2026-01-05"})
    assert client.delete("/members/gita").status_code == 200
    assert client.get("/members").json() == []
    assert client.delete("/members/gita").status_code == 404
