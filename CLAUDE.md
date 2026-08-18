# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Tasks

**Setup**
```bash
pip install -e ".[dev]"
python -m brewd.seed brewmaster.db
```

**Run the app**
```bash
BREWD_DB=brewmaster.db uvicorn brewd.api:app --reload
```

**Tests**
```bash
pytest  # All tests
pytest tests/test_rounds.py  # Single file
pytest tests/test_rounds.py::test_debt_logic  # Single test
```

**Linting**
Ruff is configured with 90-character line limits.

**Schema checks**
```bash
brewd doctor  # Validates ledger consistency
```

## Code Architecture

1. **API layer** (FastAPI) - Endpoints for rounds, members, and status tracking
   - Endpoints:
     - `GET /health`: Check service availability
     - `GET/POST /members`: Manage member registry
     - `GET/POST /rounds`: Track tea rounds
     - `GET /status`: View brew debt balances
     - `GET /next`: Calculate next round maker
     - `GET /leaderboard`: Quarterly round rankings
2. **SQLite database** - No migrations, schema created on connect
   - Tables:
     - `members`: id, name, brew_debt, biscuit_balance
     - `rounds`: id, maker_id, timestamp, cost_in_pence
   - Relationships:
     - Rounds reference members via maker_id
     - Ledger balances are derived from round history
3. **Core logic** - Brew debt calculations and biscuit money tracking
   - Money is stored as integer pence to avoid floating-point errors
   - Fairness algorithm:
     - Brew debt = (rounds received - rounds made)
     - Fair share = team average brew debt
     - `/next` endpoint selects the member furthest above fair share
4. **Test structure** - `tests/` directory with focused unit tests
   - Test patterns:
     - Integer pence validation in all financial operations
     - Ledger consistency checks in `test_ledger.py`
     - API contract tests in `test_api.py`
5. **CLI utilities** - `brewd.seed` and `brewd doctor` for operations
   - `brewd doctor`: Validates ledger consistency between rounds and member balances

The system maintains fairness through a ledger that tracks:
- Rounds made vs received (brew debt)
- Biscuit balances in integer pence

Endpoints are documented in the README with usage examples. The API uses a simple model where GET operations retrieve state and POST operations modify it.