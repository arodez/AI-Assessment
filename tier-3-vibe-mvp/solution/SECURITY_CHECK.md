# Security Check

Applied the vibe-coding security checklist before treating this MVP as done.
Checked by reading the code and by exercising the running app with a headless
browser (Playwright) driving real requests through the UI.

## 1. Secrets / API keys in code

- **Checked:** grepped `src/` and `public/` for hardcoded passwords, tokens,
  connection strings.
- **Found:** none in application code. `ORGANIZER_PASSWORD` and
  `SESSION_SECRET` are read from `process.env` only.
- **Fixed/confirmed:** `.env` (the file with real values) is listed in
  `.gitignore`; only `.env.example` (placeholder values, clearly named
  `changeme`) is committed. `server.js` refuses to start if either env var is
  missing, so a real deployment can't silently run with no password.

## 2. Input validation

- **Checked:** malformed email, empty/negative/zero capacity, empty title,
  past event date, oversized title/description, non-integer capacity.
- **Found:** all of these were already handled server-side in
  `src/validation.js` (not just client-side `required` attributes, which are
  trivially bypassed) — confirmed by posting directly to `/api/events` and
  `/api/events/:id/signup` and seeing 400s with clear messages for each case.
- **Fixed:** nothing further needed; this was correct on first pass. See
  `VERIFICATION_NOTE.md` for the two things that were **not** correct on
  first pass.

## 3. No unintended data exposure

- **Checked:** does `GET /api/events` (the public list) ever include attendee
  emails or names? Can an attendee reach organizer-only data without the
  password?
- **Found:** the public endpoint only ever selects/returns
  `id, title, description, event_date, capacity, spotsRemaining` — attendee
  rows are never joined into that response. Organizer routes
  (`/api/organizer/*`) are behind `requireOrganizer` middleware that checks
  the signed session cookie; hitting them without a valid session returns 401
  with no attendee data in the body.
- **Fixed:** nothing further needed after confirming via direct requests
  (with and without a valid organizer session).

## 4. Cross-site scripting (XSS)

- **Checked:** submitted `<script>window.__xss=true</script>` as an event
  title and `<img src=x onerror="...">` as a description.
- **Found a real issue and fixed it** — see `VERIFICATION_NOTE.md` mistake #2
  for the full story: the first implementation escaped HTML entities
  server-side *and* rendered everything through `textContent` client-side,
  which is redundant (`textContent` alone is already XSS-safe) and produced
  double-escaped, broken-looking text (`&lt;script&gt;`) for any title with
  special characters. Removed the server-side escaping; `textContent`
  rendering is now the single, sufficient layer. Re-tested the same payloads
  — script never executes, and the text now displays exactly as typed.

## 5. Cross-origin request exposure

- **Checked:** is the API reachable from another origin/site, or only from
  this app's own pages?
- **Found:** no CORS middleware is present, so the browser's default
  same-origin policy applies — no `Access-Control-Allow-Origin` header is
  ever sent, meaning other sites' JS cannot read responses from this API.
  The organizer session cookie is set `httpOnly` and `sameSite: strict`.
- **Fixed:** nothing further needed; this was a deliberate constraint from
  the start (see `BRIEF.md`), confirmed present in `src/server.js`.

## 6. SQL injection

- **Checked:** all database access in `src/routes/*.js` and `src/db.js`.
- **Found:** every query uses `better-sqlite3` prepared statements with `?`
  placeholders; no user input is string-concatenated into SQL.
- **Fixed:** nothing needed.

## Known limitations (accepted for MVP scope, not fixed)

- **Shared organizer password is a single shared secret**, not per-organizer
  auth — anyone with the password can create events and see every event's
  attendee list. Acceptable for an internal MVP with a small trusted
  organizer group; would need real per-user accounts before wider rollout.
- **No brute-force protection / rate limiting** on the organizer login
  endpoint. Low risk at MVP scale but worth adding before production.
- **No CSV formula-injection guarding** — a name/email starting with `=`,
  `+`, `-`, or `@` is quoted correctly as a CSV value but not neutralized
  against spreadsheet-formula execution if opened in Excel/Sheets. Noted,
  not fixed, since it's outside the stated requirements and low severity for
  internal event sign-ups.
- **In-memory rate of duplicate/overlap checks** relies on SQLite being
  single-process; this MVP is not designed to be horizontally scaled.
