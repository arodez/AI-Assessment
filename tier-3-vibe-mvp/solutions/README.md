# Community Events Hub — MVP

A small internal app for publishing events (study groups, AMAs, workshops) and
letting people RSVP. Built for the "Community Events Hub" MVP assignment.

## Requirements

- **Node.js ≥ 22.5.0** (this app uses the built-in `node:sqlite` module, which
  is only available from Node 22.5 onward). Verify with `node --version`.
- No `npm install` needed — **this app has zero external dependencies.**
  (See "Why no dependencies?" below for why.)

## Running it

```bash
cd app
node server.js
```

You should see:

```
Community Events Hub running at http://localhost:3000
[WARN] ORGANIZER_TOKEN not set — using insecure dev default. Set it in .env for real use.
```

(The `ExperimentalWarning: SQLite is an experimental feature` line is expected
— it comes from Node itself, not a bug in this app.)

Then open **http://localhost:3000** in a browser.

A SQLite database file (`data.sqlite`) is created automatically on first run,
in the `app/` folder, right next to `server.js`. Delete it to reset all data.

## Setting the organizer token

The organizer-only pages (attendee lists, CSV export) are protected by a
shared token, not full user accounts (see `BRIEF.md` for why this is an
intentional MVP-scope limitation).

By default, if you don't set anything, the app falls back to the token
`dev-only-change-me` — fine for trying it out locally, **not fine for any
real deployment.**

To set a real token:

```bash
cp .env.example .env
# then edit .env and set ORGANIZER_TOKEN to something private
```

Then visit `http://localhost:3000/organizer` and enter that token.

## Using the app

- **Anyone:** visit `/` to see upcoming events sorted by date, with spots
  remaining. Click into an event to RSVP with your name and email.
- **Organizers:** visit `/organizer`, enter the token, and you'll see every
  event with signup counts. Click into one to see the full attendee list and
  export it as a CSV.

## Project structure

```
app/
  server.js              — HTTP server, routing, organizer auth
  loadEnv.js              — tiny manual .env file loader (see below)
  validation.js           — all server-side input validation rules
  db/
    index.js              — SQLite schema + queries (node:sqlite)
  views/
    escape.js             — HTML-escaping helper (used everywhere user input is rendered)
    layout.js              — shared page shell + CSS
    eventsList.js           — public event list page
    eventDetail.js          — single event + RSVP form
    eventCreate.js           — create-event form
    organizerLogin.js        — organizer token entry page
    organizerDashboard.js     — organizer's list of all events
    organizerEventAttendees.js — per-event attendee list + CSV export link
  .env.example            — template for setting ORGANIZER_TOKEN / PORT
  .gitignore               — keeps .env, node_modules/, and data.sqlite out of version control
```

## Known limitations (by design, for MVP scope)

- **Organizer auth is a single shared token, not real accounts.** The token
  is passed via a URL query string (`?token=...`) for simplicity, which means
  it can end up in browser history or server logs. Fine for an internal
  prototype; would need to move to header/cookie-based session auth for
  production. See `SECURITY_CHECK.md` for the full writeup.
- **`node:sqlite` is an experimental Node API.** It could change in a future
  Node release. Chosen here because it requires zero external dependencies —
  useful in this specific build environment (see "Why no dependencies?").
- **No email confirmation is sent on RSVP.** Sign-up is instant and
  synchronous; there's no email-sending integration in this MVP.
- **Persistence is a single SQLite file**, not something like Postgres — fine
  for an MVP, would need a real DB + migrations for production scale.

## Why no dependencies?

The original plan (see `BRIEF.md`) was Express + `better-sqlite3` + EJS. While
building, `npm install` failed because the build environment had no network
access to the npm registry. Rather than write untested code assuming
packages that couldn't actually be verified, the app was rewritten to use
only Node's built-in `http` and `node:sqlite` modules, plus small hand-written
helpers for templating and `.env` loading. This is documented as a deviation
in `PROMPT_LOG.md`. The upshot: this app runs with just `node server.js` and
no install step at all, which also makes it trivial to run for grading.
