# Community Events Hub

An internal mini-app for publishing events (study groups, AMAs,
workshops) and letting people RSVP. Flask + SQLAlchemy + SQLite API,
React + TypeScript SPA frontend. See [`BRIEF.md`](BRIEF.md) for the full
product brief (requirements, technical design, edge cases, acceptance
criteria) and [`PROMPT_LOG.md`](PROMPT_LOG.md) for the record of prompts
used to build it.

## Prerequisites

- Python 3.12+ and [Poetry](https://python-poetry.org/) 2.x (backend)
- Node.js ^26.0.0 (frontend) — an asdf `.tool-versions` pinning
  `nodejs 26.6.0` lives in `frontend/`; `asdf install` picks it up
  automatically once you `cd` there if you use asdf

## Quick start

Two terminals, both from a clean checkout:

```bash
# Terminal 1 — backend (http://localhost:5000)
cd solution/backend
poetry install
cp .env.example .env
poetry run flask db-setup
poetry run flask run
```

```bash
# Terminal 2 — frontend (http://localhost:5173)
cd solution/frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173` — you'll land on `/login`. Log in with any
seeded email below (no password, no account creation — this MVP's auth
is intentionally minimal, see `BRIEF.md`).

### Seeded accounts

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

Admin accounts can create events and view the organizer attendance
screen; attendee accounts can browse the feed and RSVP.

### Ports

| Service | Port | Notes |
|---|---|---|
| Backend (Flask) | `5000` | `VITE_API_BASE_URL` in the frontend's `.env` must match this |
| Frontend (Vite) | `5173` | Matches the backend's default `CORS_ALLOWED_ORIGINS` |

### Resetting to a clean slate

```bash
cd solution/backend
rm -rf instance uploads
poetry run flask db-setup
```

The frontend has no persistent server-side state of its own — a
`localStorage` clear (or "Switch account" in the app header) is enough
to reset its auth state.

## Persistence

SQLite via SQLAlchemy + Alembic, not in-memory — see
[`backend/docs/DATABASE.md`](backend/docs/DATABASE.md) for the schema
and seed data.

## Further docs

- [`BRIEF.md`](BRIEF.md) — product brief (requirements, edge cases, acceptance criteria)
- [`PROMPT_LOG.md`](PROMPT_LOG.md) — prompt/iteration history
- [`SECURITY_CHECK.md`](SECURITY_CHECK.md) — manual security pass (secrets, input validation, data exposure)
- [`VERIFICATION_NOTE.md`](VERIFICATION_NOTE.md) — manually verified flows, including a real mistake caught along the way
- [`backend/README.md`](backend/README.md) — backend setup, environment variables, code quality commands
- [`backend/docs/API.md`](backend/docs/API.md) — full endpoint reference
- [`backend/docs/DATABASE.md`](backend/docs/DATABASE.md) — schema reference, ER diagram
- [`frontend/README.md`](frontend/README.md) — frontend setup, project layout, known simplifications vs. the mockups
