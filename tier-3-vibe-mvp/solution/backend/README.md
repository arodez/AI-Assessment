# Community Events Hub — Backend

Flask + SQLAlchemy + SQLite backend for the Community Events Hub MVP:
JWT auth, the full REST API (events, registrations, organizer
attendance/CSV export), schema/data managed by Alembic. No frontend here
yet — see [`../../BRIEF.md`](../../BRIEF.md) for the overall product spec.

- [`docs/DATABASE.md`](docs/DATABASE.md) — full schema reference, ER diagram, migration workflow.
- [`docs/API.md`](docs/API.md) — full endpoint reference, auth flow, error codes.

## Prerequisites

- Python 3.12+ (developed against 3.14)
- [Poetry](https://python-poetry.org/) 2.x

## Setup

```bash
poetry install
cp .env.example .env   # defaults are fine as-is; only edit if you need to
                        # point at a different DB/upload location, or to
                        # override JWT_SECRET_KEY outside local dev
poetry run flask db-setup
```

`flask db-setup` creates `instance/` and `uploads/events/` if missing, then
runs Alembic migrations to `head` — which builds the schema and loads the
seed data in one step. It's idempotent: safe to run again on an
already-set-up database (it's a no-op).

To start over from scratch:

```bash
rm -rf instance uploads
poetry run flask db-setup
```

## What you get after setup

- `instance/app.db` — SQLite database with 8 seeded users and 35 seeded
  events spanning Aug–Dec 2026, weighted toward the near term (see
  [`docs/DATABASE.md`](docs/DATABASE.md#seed-data)).
- `uploads/events/` — the 7 event cover photos, copied from
  `../../mockups/project/assets/photos/`.

### Seeded accounts

Login only works against these — account creation is out of scope for
this MVP (see `docs/API.md`):

| Email | Role |
|---|---|
| `alice.kim@company.com` | admin |
| `priya.shah@company.com` | admin |
| `diego.ramirez@company.com` | attendee |
| `maria.chen@company.com` | attendee |
| `sam.oneil@company.com` | attendee |
| `jordan.lee@company.com` | attendee |
| `taylor.brooks@company.com` | attendee |
| `noah.patel@company.com` | attendee |

## Running the API

```bash
poetry run flask run
```

```bash
# Log in as a seeded admin, capture the token
TOKEN=$(curl -s -X POST localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"email": "alice.kim@company.com"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

# List upcoming events
curl -s localhost:5000/events -H "Authorization: Bearer $TOKEN"
```

Full endpoint reference, request/response shapes, and error codes:
[`docs/API.md`](docs/API.md).

Or import [`postman/community-events-hub.postman_collection.json`](postman/community-events-hub.postman_collection.json)
+ [`postman/local.postman_environment.json`](postman/local.postman_environment.json)
into Postman (or run headlessly via `newman`) — see
[`postman/README.md`](postman/README.md).

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///instance/app.db` | Rarely needs overriding locally |
| `UPLOAD_FOLDER` | `uploads/events/` | Where cover photos are stored |
| `JWT_SECRET_KEY` | a placeholder dev value | **Must** be overridden to a real secret outside local dev — never commit a real value |
| `JWT_ACCESS_TOKEN_EXPIRES_HOURS` | `24` | Token lifetime; no refresh flow in this MVP |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Comma-separated list, for the future React frontend |
| `MAX_CONTENT_LENGTH_MB` | `6` | Hard request-body cap, ahead of the 5MB app-level image check |

## Running tests

```bash
poetry run pytest
```

Tests build their own scratch SQLite DB and upload folder per test (via
`db.create_all()`, not Alembic — see `tests/conftest.py` for why), so they
never touch `instance/app.db` or the real `uploads/events/`. Coverage
reports automatically (`--cov`, floor at 85%; currently ~96%).

## Code quality

```bash
poetry run ruff check .      # lint
poetry run black --check .   # format check (drop --check to auto-format)
poetry run mypy app          # type check
poetry run pytest            # tests + coverage
poetry run pre-commit run --all-files   # all of the above, plus trailing-whitespace/EOF hooks
```

`pre-commit` here is config-only, **not installed as a git hook** — the
real git repo root is the parent monorepo, which already has an unrelated
project's pre-commit hook installed there. Run it manually as shown above.

## Working with migrations

Alembic is the source of truth for schema *and* the initial seed data —
not `db.create_all()` (see [`docs/DATABASE.md`](docs/DATABASE.md#migrations)
for why). Common commands, run from this directory:

```bash
poetry run alembic current              # what revision is the DB on
poetry run alembic history               # list all revisions
poetry run alembic revision --autogenerate -m "describe the change"
poetry run alembic upgrade head          # apply pending migrations
poetry run alembic downgrade base        # roll everything back
```

## Project layout

```
app/
  routes/       Flask blueprints — auth, events, attendance, registrations
  schemas/      Pydantic request validation (LoginRequest, EventCreateRequest)
  services/     image_processing.py (cover-photo validation/re-encode), csv_export.py
  models/       SQLAlchemy models
  auth.py       admin_required decorator, JWT identity helpers
  errors.py     Error envelope + Flask-JWT-Extended callbacks
  cli.py        `flask db-setup`
  config.py     App config, runtime paths
  extensions.py db / jwt / cors singletons
migrations/     Alembic — versions/0001 (schema), versions/0002 (seed data)
scripts/        seed_data.py — the actual fixture data + photo-copy helper
tests/          pytest — model + route + schema + image-processing coverage
docs/           DATABASE.md, API.md
postman/        Importable Postman collection + environment
instance/       SQLite DB file (git-ignored, created by `flask db-setup`)
uploads/events/ Seeded/uploaded cover photos (git-ignored, ditto)
```
