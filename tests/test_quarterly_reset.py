from brewd import ledger
from brewd.rounds import next_brewer, record_round, round_history, start_new_quarter


def test_new_quarter_wipes_the_old_history(db):
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    record_round(db, "bob", drinkers=["alice", "bob", "carol"])
    start_new_quarter(db)
    makers = sorted(r["maker"] for r in round_history(db))
    assert makers == ["alice", "bob", "carol"]


def test_nobody_starts_the_quarter_in_credit(db):
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    start_new_quarter(db)
    debts = ledger.all_debts(db)
    assert len(set(debts.values())) == 1


def test_the_rota_still_works_after_a_reset(db):
    record_round(db, "alice", drinkers=["alice", "bob", "carol"])
    start_new_quarter(db)
    assert next_brewer(db) in {"alice", "bob", "carol"}
