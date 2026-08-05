# Product Brief — Community Events Hub (MVP)

## What & For Whom

We're building an internal MVP called **Community Events Hub** for the communities team.
It lets team members publish internal events (study groups, AMAs, workshops) and lets
other employees sign up (RSVP) for them. There is currently no repo, no design, and no
backend — this is being built from scratch.

Two user types:
- **Attendees** — browse upcoming events and sign up with name + email. No login required.
- **Organizers** — create events and view/export the attendee list for events they manage.
  Access is gated by a shared token (not full user accounts — see Constraints).

## Functional Requirements

1. **Create event** — an organizer can create an event with:
   - Title (required)
   - Date (required)
   - Description (optional)
   - Maximum capacity (required, positive integer)

2. **Sign-up (RSVP)** — an attendee can sign up for an event with name + email:
   - Email must be valid format
   - No duplicate sign-ups per event (same person can't RSVP twice to the same event)
   - Clear rejection message when the event is already at capacity

3. **Public list** — anyone can see a list of upcoming events, sorted by date ascending,
   showing title, date, description, and **spots remaining** (capacity − current
   sign-ups). This view must NOT show attendee names or emails.

4. **Organizer view** — token-gated. Per event, shows the full attendee list (name,
   email, sign-up timestamp) and allows CSV export (name, email, timestamp).

## Technical Constraints

- **Stack:** Node.js (backend), SQLite via the built-in `node:sqlite` module
  (persistence), hand-rolled server-rendered HTML templates (frontend) — no
  separate frontend build step, no frontend framework.
  > **Note:** the original brief specified Express + `better-sqlite3` + EJS.
  > During implementation, the execution environment had no network access to
  > run `npm install`, so the stack was changed to use only Node's built-in
  > `http` and `node:sqlite` modules — zero external dependencies. This is
  > documented as a deviation in PROMPT_LOG.md. `node:sqlite` is an
  > experimental Node API (requires Node ≥22.5) — flagged as a limitation.
- **Persistence:** SQLite file on disk (`data.sqlite` or similar), NOT in-memory —
  data survives server restarts. This is a step above the MVP's minimum bar
  (in-memory) but still lightweight.
- **Organizer auth:** a single shared token read from an environment variable
  (`ORGANIZER_TOKEN`), with a hardcoded fallback default in code for local dev
  convenience. This is explicitly NOT real authentication (no per-organizer
  accounts, no password hashing, no sessions) — this is a known, documented MVP
  limitation, acceptable for an internal tool prototype but NOT production-ready.
- **What NOT to do:**
  - Do not store secrets or tokens directly in committed code — the fallback
    token is a clearly-labeled placeholder, real deployments must override it
    via `.env` (which must be gitignored).
  - Do not expose attendee emails/names on any public (non-organizer) route or
    API response.
  - Do not build user accounts, email sending, payment, or any feature beyond
    the 4 functional requirements above — MVP scope only.
  - Do not trust client-side validation alone — every rule must be re-enforced
    server-side.
  - Do not use string-concatenated SQL — all queries must be parameterized.

## Validation Rules

| Field | Rule |
|---|---|
| Event title | Required, non-empty after trim, max 200 chars |
| Event date | Required, valid date, must be today or in the future |
| Event description | Optional, max 2000 chars |
| Event capacity | Required, positive integer (reject 0, negative, decimals, non-numeric) |
| Attendee name | Required, non-empty after trim |
| Attendee email | Required, valid email format; normalized (trim + lowercase) before storage and before duplicate check |
| Duplicate check | Case-insensitive, whitespace-trimmed match on email, scoped per event |
| Full event | Reject RSVP when spots remaining = 0, with a clear error message |

## Edge Cases to Handle

- Zero, negative, or non-numeric capacity on event creation
- Empty or whitespace-only title
- Past date on event creation
- Malformed email (`"foo"`, `"foo@"`, `"@bar.com"`, empty string)
- Duplicate email with different casing/whitespace (`"Foo@X.com "` vs `"foo@x.com"`)
- RSVP attempt on an event that's already full
- RSVP attempt on a nonexistent event ID
- SQL injection attempts in any text field (title, description, name)
- XSS attempts in any text field (must be escaped on render)
- Organizer routes accessed without a valid token

## Acceptance Criteria (Definition of Done)

The MVP is done when, starting only from the README's setup instructions:

1. A fresh clone/install + `npm start` boots the app with no manual DB setup steps.
2. An organizer can create an event via the UI and see it appear in the public list.
3. An attendee can successfully RSVP to an event with open capacity, and the
   spots-remaining count decrements immediately.
4. RSVPing to a full event is rejected with a clear, user-visible error.
5. RSVPing twice with the same email (any casing/whitespace) to the same event
   is rejected with a clear, user-visible error.
6. The public event list never exposes attendee names or emails in HTML or any
   API response.
7. The organizer view is inaccessible without the correct token, and shows the
   correct attendee list + working CSV export when accessed with it.
8. All validation rules above are enforced server-side, confirmed by manually
   triggering each edge case and observing correct rejection (not a crash).
9. No secrets are committed to the repo; `.env` is gitignored.
