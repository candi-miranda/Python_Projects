# Flight Range API

A small REST API that answers one question: **can this aircraft fly
non-stop between these two airports?**

Given an aircraft's performance data and two airports, it computes the
great-circle distance between them and compares it against the
aircraft's maximum cruise range (via the Breguet range equation) to
return a feasible/not-feasible verdict with a margin.

Built as a backend/software-engineering portfolio piece — the interesting
part isn't the aerospace maths (that's a couple of pure functions), it's
the API design, data layer, and test suite around it.

## Stack

Python 3, FastAPI, SQLAlchemy, SQLite (swappable for PostgreSQL), pytest, Docker.

## Architecture

```
app/
├── main.py       # FastAPI routes
├── models.py     # SQLAlchemy ORM models (Aircraft, Airport)
├── schemas.py    # Pydantic request/response validation
├── crud.py       # DB access functions
├── geo.py        # Pure functions: great-circle distance, Breguet range
└── database.py   # Engine/session config

tests/
├── test_geo.py   # Unit tests for the pure math (no DB, no HTTP)
└── test_api.py   # Integration tests against the running API
```

The math (`geo.py`) is deliberately kept free of any DB or HTTP
dependency, so it's trivial to unit test in isolation. The API/DB layers
are tested separately with an in-memory SQLite database per test, so
tests never share state or touch a real database.

## Running locally

```bash
pip install -r requirements.txt
python seed_data.py          # populates a couple of example aircraft/airports
uvicorn app.main:app --reload
```

API docs (interactive): http://localhost:8000/docs

## Running with Docker

```bash
docker build -t flight-range-api .
docker run -p 8000:8000 flight-range-api
```

## Running tests

```bash
pytest -v
```

Tests run automatically on every push via GitHub Actions (`.github/workflows/ci.yml`).

## Example

```bash
curl "http://localhost:8000/route/LPPT/LPPD/feasibility?aircraft_name=ATR%2072-600"
```

```json
{
  "origin": "LPPT",
  "destination": "LPPD",
  "aircraft": "ATR 72-600",
  "great_circle_distance_km": 1448.7,
  "max_range_km": 5351.7,
  "feasible": true,
  "margin_km": 3903.0
}
```

## Endpoints

| Method | Path                                        | Description                          |
|--------|---------------------------------------------|---------------------------------------|
| GET    | `/health`                                   | Liveness check                        |
| POST   | `/aircraft`                                 | Add an aircraft                       |
| GET    | `/aircraft`                                 | List all aircraft                     |
| GET    | `/aircraft/{id}`                            | Get one aircraft                      |
| POST   | `/airports`                                 | Add an airport                        |
| GET    | `/airports`                                 | List all airports                     |
| GET    | `/route/{origin}/{destination}/feasibility` | Check if a route is flyable           |

## Possible extensions

- Swap SQLite for PostgreSQL (`DATABASE_URL` env var already supports it)
- Add authentication (API keys / OAuth2)
- Add pagination on list endpoints
- Replace the hand-seeded aircraft/airport data with a real dataset (e.g. OurAirports)
