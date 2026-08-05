# Security Check

> Applied before considering the MVP "shareable." Every item below was actually tested against the running app (see PROMPT_LOG.md Increments 3–5 and VERIFICATION_NOTE.md for evidence), not just reasoned about in the abstract.

## 1. No secrets or API keys in the code

**Checked:** grepped the codebase for hardcoded credentials, and reviewed how the organizer token is handled.

**Finding:** the organizer token has a hardcoded *fallback* value (`dev-only-change-me`) in `server.js`, used only when `ORGANIZER_TOKEN` isn't set in the environment. This is a deliberate, labeled placeholder for local dev convenience — not a real secret, since it's meant to be overridden.

**Fixed / mitigated:**
- The real token is loaded from `.env` (via a hand-rolled loader in `loadEnv.js`, since the `dotenv` package wasn't installable — see PROMPT_LOG.md Prompt 3), never committed.
- `.env` is listed in `.gitignore`.
- The server logs a visible `[WARN]` on boot if `ORGANIZER_TOKEN` isn't set, so it's hard to accidentally deploy with the insecure default without noticing.
- **Residual limitation, documented, not fixed:** this is a single shared token, not per-user auth, and it's passed via URL query string (`?token=...`) for simplicity. That means the token can end up in browser history, server access logs, or a Referer header if a link is shared carelessly. Acceptable for an internal MVP prototype; **not acceptable for production** without moving to a proper session-based auth model with the token in a header or cookie instead of the URL.

## 2. Input validation

**Checked:** every field on both the "create event" and "RSVP" forms, tested against malformed input (see Increment 5 in PROMPT_LOG.md for the full list of 15 validation edge cases run).

**Findings & fixes, by field:**
| Field | What was tested | Result |
|---|---|---|
| Event capacity | negative, zero, decimal, non-numeric | All rejected with 400 + "Capacity must be a positive whole number." Enforced in `validation.js`, server-side — not just an HTML `min="1"` attribute, which a client can bypass. |
| Event title | empty, whitespace-only | Both rejected with 400 + "Title is required." Trimmed before the emptiness check, so `"   "` doesn't slip through. |
| Event date | past date | Rejected with 400 + "Event date must be today or in the future." |
| RSVP email | no `@`, trailing `@`, leading `@`, empty | All rejected with 400 + appropriate message. Regex is intentionally conservative — good enough to catch obviously malformed input without trying to be a full RFC 5322 validator. |
| RSVP name | empty | Rejected with 400 + "Name is required." |
| Nonexistent event ID | RSVP to `/events/9999/rsvp`, GET `/events/9999`, GET `/events/abc` | All correctly return 404, no crash, no stack trace leaked to the client. |

All validation lives in `validation.js` and runs server-side on every request — HTML `required`/`type="email"`/`min` attributes exist too, but only as a UX nicety, never trusted as the actual gate.

## 3. No data exposure

**Checked:** whether an attendee (or anyone on the public routes) can see other attendees' emails or names.

**Finding:** initially, this was a design requirement from the brief, not yet a tested one. Verified explicitly (see Increment 5 in PROMPT_LOG.md): seeded an event with an attendee using a distinctive name and email, then grepped both the public homepage and the public event-detail page for any trace of that data. **None found in either.** The public routes' SQL queries (`listUpcomingEventsWithSpots`, `listAllEventsWithSpots`) only ever `SELECT` event fields and an aggregate signup count — they never `JOIN` in attendee names or emails, so there's no code path that could leak this data even if a template were miswritten.

**Also checked:** the reverse — can an unauthenticated request reach the organizer attendee-list or CSV-export routes? Tested with no token, and with a wrong token, against both `/organizer/events/:id` and `/organizer/events/:id/export.csv` — both correctly return `401` with no attendee data in the response body.

**Fixed:** N/A — this was correct by design from the initial schema/query separation (public queries never touch the `attendees` table's PII columns), confirmed by testing rather than assumed.

## 4. Injection & XSS (extra checks beyond the brief's checklist)

Since this app has no framework doing automatic escaping (no EJS — see the stack deviation noted in PROMPT_LOG.md Prompt 3), these were checked explicitly rather than assumed safe:

- **XSS:** `<script>alert(1)</script>` as an event title, and `<img src=x onerror=alert(1)>` as an RSVP name, were both stored as-is but rendered HTML-escaped (`&lt;script&gt;`, `&lt;img src...`) via a shared `escapeHtml()` helper used on every user-supplied value in every view. Confirmed on both the public list and the organizer attendee view.
- **SQL injection:** a title containing `'; DROP TABLE events; --` was submitted. All database access uses parameterized queries (`db.prepare(...).run(...)`/`.get(...)`/`.all(...)` with `?` placeholders) — never string concatenation — so the payload was stored and displayed as inert text, and the `events` table remained fully intact afterward (confirmed the homepage still loaded correctly post-injection-attempt).

## Summary

Nothing was found that required an actual code fix beyond what was already built correctly in Increments 2–3 — the one real gap (organizer token in the URL query string, no session/cookie-based auth) is a known, explicitly documented MVP limitation rather than an oversight, consistent with what BRIEF.md scoped as acceptable for this iteration.
