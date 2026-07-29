# Community Events Hub

A minimal internal events app: publish events, let people RSVP, show a public
list of upcoming events with spots remaining, and give organizers a
password-gated view of attendees per event with CSV export.

## Stack

- Node.js + Express (backend)
- Vanilla HTML/CSS/JS (frontend, no framework)
- SQLite via `better-sqlite3` (file-based persistence, survives restarts)

## Setup

```bash
npm install
cp .env.example .env
```

Edit `.env` and set a real `ORGANIZER_PASSWORD` and `SESSION_SECRET`
(the app refuses to start if either is missing).

## Run

```bash
npm start
```

Then open:
- **Public event list:** http://localhost:3000/
- **Organizer view:** http://localhost:3000/organizer.html — log in with the
  password set in `.env` as `ORGANIZER_PASSWORD`.

## Reset the app (for a full manual re-test)

The only state is the SQLite file (events + attendees) and, separately, the
organizer login session stored in a browser cookie. To get back to a
completely clean slate:

```bash
# 1. Stop the server (Ctrl+C, or if backgrounded):
lsof -ti:3000 -sTCP:LISTEN | xargs kill

# 2. Delete the database (and its WAL/SHM sidecar files, since the app runs
#    in WAL journal mode):
rm -f data/events.db data/events.db-wal data/events.db-shm

# 3. Restart:
npm start
```

This recreates an empty `events`/`attendees` schema on next boot (see
`src/db.js`) — no events, no attendees.

To reset just the **organizer login** without touching data, click "Log out"
in the organizer view, or clear the `organizer_session` cookie for
`localhost:3000` in your browser.

## Data model

SQLite file lives at `data/events.db` (created automatically on first run).

- `events`: `id, title, description, event_date, capacity, created_at`
- `attendees`: `id, event_id, name, email, created_at`, with a
  `UNIQUE(event_id, email)` constraint (case-insensitive — emails are
  lowercased before storage/comparison) enforcing no duplicate sign-ups per
  event at the database level, in addition to an app-level check that
  produces a clean error message.

## Known limitations (documented per the MVP brief)

- **Persistence is a single SQLite file** — fine for an MVP, not designed for
  concurrent multi-instance deployment.
- **Organizer gating is one shared password**, not per-user accounts. Anyone
  with the password can create events and view/export every event's
  attendee list. See `SECURITY_CHECK.md` for the full tradeoff discussion.
- **No email verification or account system for attendees** — sign-up is
  just name + email, by design (see `BRIEF.md`).
- **Event "overlap" has no real duration field** — the MVP treats two events
  within 2 hours of each other as overlapping, since there's no
  start/end-time range in the data model. Creating an overlapping event
  prompts an organizer confirmation rather than blocking it outright.
- **No rate limiting** on the organizer login endpoint.
- **No CORS support** — the API is intentionally only reachable from this
  app's own frontend (same-origin), not from external scripts/sites.
- **Organizer session cookie is stateless and survives a server restart** —
  it's a signed `cookie-session`, not backed by any server-side store, so
  restarting the server does not force organizers to log in again as long as
  `SESSION_SECRET` is unchanged and the cookie hasn't hit its 8h `maxAge`.
  See `SECURITY_CHECK.md` for the invalidation options considered and the
  recommended fix if this is ever picked up.

## Process documentation

- [`BRIEF.md`](BRIEF.md) — the initial prompt, written before any code.
- [`PROMPT_LOG.md`](PROMPT_LOG.md) — every prompt sent during the build.
- [`SECURITY_CHECK.md`](SECURITY_CHECK.md) — the security checklist pass.
- [`VERIFICATION_NOTE.md`](VERIFICATION_NOTE.md) — the 3 required test flows
  plus mistakes caught during the build.
