def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "brewing"


def test_add_and_list_members(client):
    client.post("/members", json={"name": "gita", "joined": "2026-01-05"})
    client.post("/members", json={"name": "hugo", "joined": "2026-01-06"})
    names = [m["name"] for m in client.get("/members").json()]
    assert names == ["gita", "hugo"]


def test_duplicate_member_is_rejected(client):
    client.post("/members", json={"name": "gita"})
    assert client.post("/members", json={"name": "gita"}).status_code == 409


def test_unknown_maker_is_rejected(client):
    assert client.post("/rounds", json={"maker": "nobody"}).status_code == 404


def test_recording_a_round_moves_the_debt(client):
    for name in ("gita", "hugo", "ida"):
        client.post("/members", json={"name": name, "joined": "2026-01-05"})
    resp = client.post(
        "/rounds", json={"maker": "gita", "drinkers": ["gita", "hugo", "ida"]}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["maker"] == "gita"
    assert sorted(body["drinkers"]) == ["gita", "hugo", "ida"]

    status = client.get("/status").json()
    owed = {m["name"]: m["owes_rounds"] for m in status["members"]}
    assert owed == {"gita": 0, "hugo": 1, "ida": 1}
