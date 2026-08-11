# Security Check

A manual pass against the running app (backend on `:5000`, seeded data), covering the areas CLAUDE.md calls out at minimum, plus a couple of adjacent checks that came up naturally while doing it. Every claim below was actually run against the live server on 2026-08-11, not inferred from reading the code — commands are included so they can be re-run.

## 1. No secrets or API keys in code

```bash
git grep -niE "(api[_-]?key|secret[_-]?key|password\s*=|token\s*=\s*['\"]|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z]+ PRIVATE KEY-----)"
git ls-files | grep -E "(^|/)\.env$"
git check-ignore -v solution/backend/.env solution/frontend/.env
```

- No hardcoded credentials, API keys, or private key material anywhere in tracked files.
- No `.env` file is tracked in git, in either `solution/backend/` or `solution/frontend/`; both are correctly matched by their directory's `.gitignore`.
- `JWT_SECRET_KEY` defaults to `dev-only-change-me-not-a-real-secret-32chars` in [`app/config.py`](backend/app/config.py) — an obvious, clearly-labeled placeholder meant to be overridden via the `JWT_SECRET_KEY` env var outside local dev, documented as such in `backend/README.md`'s environment variables table. It is not a real secret checked into the repo.

## 2. Input validation

Tested directly against `POST /login` and `POST /event`, bypassing the frontend entirely (curl), to confirm the API itself — not just the UI — rejects bad input:

| Input | Result |
|---|---|
| Malformed email (`not-an-email`) on login | `400 validation_error` — "must have an @-sign" |
| Empty-string email on login | `400 validation_error` — "must not be empty" |
| Negative `spots` (`-5`) on event creation | `400 validation_error` — "spots must be a positive integer" |
| Zero `spots` (`0`) on event creation | `400 validation_error` — same message (zero isn't positive) |
| Empty `title` (`""`) on event creation | `400 validation_error` — "title must be 3-140 characters" |
| A plain-text file renamed to `.jpg`, uploaded as the cover photo | `400 validation_error` — "Uploaded file is not a valid image" |

The last one is the important one: image validation is **content-based** (Pillow actually opens and decodes the bytes), not extension- or `Content-Type`-based — a renamed non-image file is rejected server-side even though the frontend's own `CoverPhotoUpload` client-side check (which only looks at the browser-reported MIME type) would have let a similarly-renamed file through the UI. The server is the real authority here, confirmed by hitting it directly rather than trusting the client.

All of the above were re-confirmed as passing behavior in the existing automated suite too (`app/schemas/event.py`, `app/schemas/auth.py`, `app/services/image_processing.py`, and their corresponding tests) — this pass exercised the same rules live, end-to-end, rather than only trusting the test suite's own assertions.

## 3. No unintended data exposure

The specific scenario CLAUDE.md names — one attendee seeing another's email via the public list — was checked directly:

```bash
curl -s http://localhost:5000/events -H "Authorization: Bearer $ATTENDEE_TOKEN" | grep -o "@company.com" | wc -l
# -> 0
```

`GET /events` and `GET /event/:id/details` expose `host_name`/`host_team` (plain text fields on the event itself) but never an email address, and never any other attendee's registration data — confirmed by grepping the full response body for `@company.com` as an authenticated non-admin attendee and getting zero matches.

The actual attendee roster (names + emails) is only reachable via `GET /event/:id/attendance` and its CSV download, both admin-only:

```bash
curl -s http://localhost:5000/event/1/attendance -H "Authorization: Bearer $ATTENDEE_TOKEN" -w "%{http_code}"
# -> 403 forbidden

curl -s http://localhost:5000/event/1/attendance/download -H "Authorization: Bearer $ATTENDEE_TOKEN" -w "%{http_code}"
# -> 403 forbidden
```

A request with no `Authorization` header at all is rejected before touching any data:

```bash
curl -s http://localhost:5000/events
# -> 401 missing_token
```

**Frontend note**: `RequireAuth`/`RequireAdmin` route guards are UX convenience only (they just avoid rendering a page that would immediately fail every request) — the checks above confirm the real enforcement is server-side and doesn't depend on the React guards existing at all.

## 4. Scope decisions, documented rather than silently assumed

A few things below the "at minimum" bar that are worth naming explicitly as accepted MVP tradeoffs, not oversights:

- **Login has no password** — by design, per `BRIEF.md`: auth is a seeded-email allowlist plus a JWT, with account creation explicitly out of scope. This is a real simplification for an internal tool with a fixed, known user list; it would need a real credential (or SSO) before this could sit anywhere reachable outside a trusted internal network.
- **JWTs expire after 24h** (`JWT_ACCESS_TOKEN_EXPIRES_HOURS`, default `24`), no refresh flow — a stolen token is valid for at most a day, not indefinitely.
- **CORS is allowlisted**, not wide open: `CORS_ALLOWED_ORIGINS` defaults to `http://localhost:5173` only, read from the backend's `.env`.
- **Uploaded cover photos are re-encoded and EXIF-stripped** by Pillow before being written to disk under a **server-generated filename** — the client's original filename is never used for the on-disk path, closing off path-traversal via a crafted filename.
