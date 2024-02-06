import pytest

from brewd import store
from brewd.members import add_member


@pytest.fixture
def db():
    conn = store.connect()
    add_member(conn, "alice", "2019-04-01")
    add_member(conn, "bob", "2022-06-13")
    add_member(conn, "carol", "2023-02-27")
    return conn


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from brewd import api

    for table in ("drinkers", "rounds", "members", "biscuit_balances"):
        api.conn.execute(f"DELETE FROM {table}")
    api.conn.commit()
    return TestClient(api.app)
