# Brewmaster

`brewd` keeps the tea round honest.

It tracks who made the last round, who drank it, and who is therefore next. It also
splits the biscuit money so nobody ends up permanently subsidising the digestives.

## Running it

```bash
pip install -e ".[dev]"
python -m brewd.seed brewmaster.db
BREWD_DB=brewmaster.db uvicorn brewd.api:app --reload
```

Then visit <http://localhost:8000/docs>.

## API

| Method | Path | What it does |
| --- | --- | --- |
| `GET` | `/health` | Are we brewing |
| `GET` | `/members` | The register |
| `POST` | `/members` | Add someone to the register |
| `GET` | `/rounds` | Recent rounds, newest first |
| `POST` | `/rounds` | Record a round |
| `GET` | `/status` | Everyone's brew debt and biscuit balance |
| `GET` | `/next` | Whose turn it is |
| `GET` | `/leaderboard` | Rounds made this quarter, ranked |

## How the fairness maths works

Everyone carries a **brew debt**: rounds received minus rounds made. Positive means
you are in the red. The **fair share** is the team average. `GET /next` picks whoever
is furthest above the fair share, skipping the person who made the last round.

Biscuit money is held as **integer pence** throughout to avoid floating point
rounding problems, and only converted to pounds at the API boundary.

## Operations

Run `brewd doctor` to check the ledger balances and report any drift.

## Conventions

- Ruff for linting, 90 columns.
- Tests live in `tests/`, run with `pytest`.
- The database is SQLite. There are no migrations; the schema is created on connect.

## History

Originally a lunchtime hack in 2023, then rewritten when the team grew past four
people. The `members` table has been stable since then. The biscuit ledger was added
in 0.3 and has needed no changes since.
