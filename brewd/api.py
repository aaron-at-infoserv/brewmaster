from __future__ import annotations

import os
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

from brewd import ledger, rounds, store
from brewd.members import add_member, all_members, get_member


DB_PATH = os.environ.get("BREWD_DB", ":memory:")

app = FastAPI(title="brewd", version="0.4.1")
conn = store.connect(DB_PATH)


class NewMember(BaseModel):
    name: str
    joined: str | None = None
    mug: str = "unknown"

class NewRound(BaseModel):
    maker: str
    drinkers: list[str] | None = None
    biscuit_cost: float = 0.0
    made_at: str | None = None


@app.get("/health")
def health():
    return {"status": "brewing", "version": "0.4.1"}


@app.get("/members")
def list_members():
    return [
        {"name": m.name, "joined": m.joined, "mug": m.mug, "is_active": m.is_active} for m in all_members(conn)
    ]


@app.post("/members", status_code=201)
def create_member(payload: NewMember):
    if get_member(conn, payload.name) is not None:
        raise HTTPException(status_code=409, detail="already on the register")
    joined = payload.joined or datetime.now(UTC).date().isoformat()
    m = add_member(conn, payload.name, joined, payload.mug)
    return {"name": m.name, "joined": m.joined, "mug": m.mug, "is_active": m.is_active}


@app.post("/members/{name}/deactivate", status_code=200)
def deactivate_member(name: str = Path(..., description="Name of the member to deactivate")):
    member = get_member(conn, name)
    if member is None:
        raise HTTPException(status_code=404, detail=f"{name} is not on the register")
    if not member.is_active:
        raise HTTPException(status_code=400, detail=f"{name} is already inactive")

    conn.execute("UPDATE members SET is_active = 0 WHERE name = ?", (name,))
    conn.commit()

    return {"name": name, "is_active": False}


@app.post("/rounds", status_code=201)
def create_round(payload: NewRound):
    maker = payload.maker
    if not maker or not maker.strip():
        raise HTTPException(status_code=400, detail="a round needs a maker")
    maker = maker.strip()
    if get_member(conn, maker) is None:
        raise HTTPException(status_code=404, detail=f"{maker} is not on the register")

    everyone = [m.name for m in all_members(conn, active_only=True)]
    if payload.drinkers is None:
        drinkers = everyone
        assumed = True
    else:
        drinkers = []
        assumed = False
        for d in payload.drinkers:
            d = d.strip()
            if not d:
                continue
            if d not in everyone:
                raise HTTPException(
                    status_code=404, detail=f"{d} is not on the register"
                )
            if d not in drinkers:
                drinkers.append(d)
        if not drinkers:
            raise HTTPException(status_code=400, detail="nobody drank anything")
        if maker not in drinkers:
            drinkers.append(maker)

    cost = payload.biscuit_cost
    if cost < 0:
        raise HTTPException(status_code=400, detail="biscuits cannot pay you")
    if cost > 20:
        raise HTTPException(status_code=400, detail="that is not a packet of biscuits")

    made_at = payload.made_at
    if made_at is not None:
        try:
            datetime.fromisoformat(made_at)
        except ValueError:
            raise HTTPException(status_code=400, detail="made_at is not a date")

    before = {name: ledger.debt(conn, name) for name in everyone}

    round_id = rounds.record_round(
        conn,
        maker=maker,
        drinkers=drinkers,
        biscuit_cost=cost,
        made_at=made_at,
    )

    after = {name: ledger.debt(conn, name) for name in everyone}
    moved = {}
    for name in everyone:
        if before[name] != after[name]:
            moved[name] = {"was": before[name], "now": after[name]}

    biscuits = {}
    if cost:
        share = round(cost / len(drinkers), 2)
        for d in drinkers:
            biscuits[d] = {
                "charged": share,
                "balance": round(ledger.biscuit_balance(conn, d), 2),
            }
        biscuits[maker] = {
            "charged": share - cost,
            "balance": round(ledger.biscuit_balance(conn, maker), 2),
        }

    try:
        up_next = rounds.next_brewer(conn, last_maker=maker)
    except ValueError:
        up_next = None

    comment = "noted"
    if assumed:
        comment = "no drinker list given, so the whole team was assumed"
    if cost > 5:
        comment = "generous"
    if len(drinkers) == 1:
        comment = "drinking alone again"

    return {
        "round_id": round_id,
        "maker": maker,
        "drinkers": drinkers,
        "biscuit_cost": cost,
        "biscuits": biscuits,
        "debt_changes": moved,
        "next_brewer": up_next,
        "comment": comment,
    }


@app.get("/rounds")
def list_rounds(limit: int = 20):
    return rounds.round_history(conn, limit=limit)


@app.get("/status")
def status():
    debts = ledger.all_debts(conn)
    balances = ledger.all_biscuit_balances(conn)
    return {
        "fair_share": round(ledger.average_debt(conn), 3),
        "members": [
            {
                "name": name,
                "owes_rounds": debts[name],
                "biscuit_balance": round(balances.get(name, 0.0), 2),
            }
            for name in sorted(debts, key=lambda n: (-debts[n], n))
        ],
    }


@app.get("/next")
def whose_turn(last_maker: str | None = None):
    try:
        return {"next_brewer": rounds.next_brewer(conn, last_maker=last_maker)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))