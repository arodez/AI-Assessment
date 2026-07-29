# Brief — Community Events Hub (Tier 3 Vibe-Coding MVP)

> This is the finalized initial prompt, written and refined before any code was
> generated, per the process requirements in `../README.md`.

```
This repo is a collection of 5 tests to assess the use of AI for coding. We are
working ONLY inside tier-3-vibe-mvp/ and the shared ../templates/ folder — do
not touch any other folder in this repo, they are unrelated tests.

## Context
The communities team needs an MVP of the "Community Events Hub": a mini-app to
publish internal events (study groups, AMAs, workshops) and let employees sign
up. Nothing exists yet. Two user types: (1) any employee, who browses public
events and RSVPs, and (2) an organizer, who creates events and views/exports
attendee lists. Timebox: 2-3 hours of build effort — keep the implementation
proportional to that, not enterprise-grade.

## Deliverables & structure
Create everything inside a new tier-3-vibe-mvp/solution/ folder:
- solution/ — the app code itself, with its own README.md containing exact
  startup instructions (install, run, how to reach the organizer view) such
  that someone can start it from that README alone with no other context.
- solution/BRIEF.md — this prompt, refined further if needed, written BEFORE
  any code — what's being built, for whom, requirements, constraints, edge
  cases, acceptance criteria.
- solution/PROMPT_LOG.md — every prompt sent, in order, unedited, each with a
  one-line accepted/modified/rejected note (template: ../templates/PROMPT_LOG.md).
  Needs at least 3 real correction cycles with visible cause/effect — this is
  graded, don't reconstruct it after the fact.
- solution/SECURITY_CHECK.md — apply the vibe-coding security checklist before
  calling this MVP done: no secrets/API keys in code, input validation
  (malformed email, negative/zero capacity, empty title, XSS in text fields),
  no unintended data exposure (can a regular attendee see other attendees'
  emails via the public list or API responses? they should not). Document what
  you checked, what you found, what you fixed — at least one real finding.
- solution/VERIFICATION_NOTE.md — test and document at least: (a) successful
  sign-up, (b) rejection when event is full, (c) rejection of a duplicate
  email for the same event. Include at least one mistake the AI made and how
  you caught it (template: ../templates/VERIFICATION_NOTE.md).

## Functional requirements
1. Create event — title, date/time, description, maximum capacity (positive
   integer only).
2. Sign-up (RSVP) — name + email; reject malformed emails, reject duplicate
   email for the same event, reject sign-up when the event is at capacity,
   with a clear user-facing rejection message in each case.
3. Public list — upcoming events sorted by date, each showing spots
   remaining (capacity - current signups). No attendee emails or personal
   data visible on this view.
4. Organizer view — gated behind a single shared organizer password (env
   var or config value, never hardcoded/committed in plaintext to a public
   repo path — call out the tradeoff in SECURITY_CHECK.md since it's a
   shared secret, not per-user auth). Shows attendee list per event
   (name + email), exportable as CSV or copy-to-clipboard.

## Constraints (what to build with, what NOT to do)
- Stack: Node.js + Express backend, vanilla HTML/CSS/JS frontend (no
  framework). Keep it to one language.
- Persistence: SQLite (file-based), so data survives a restart. Document the
  schema briefly in the app README.
- No user accounts/sign-in system for attendees — RSVP only needs name +
  email, no password, no session for regular users.
- No third-party auth providers, no email-sending integration — out of scope
  for this MVP.
- Do not skip the security or verification passes to save time — they're
  worth 25 of the 100 points combined.
- No CORS headers enabling cross-origin access — the API is for the app's own
  frontend only, not meant to be called from arbitrary external clients.

## Edge cases to handle (and think of more as you build)
- Malformed / empty email on sign-up.
- Duplicate email signing up twice for the same event.
- Sign-up attempted when event is already full (race of the last spot should
  still reject correctly, not overbook).
- Negative, zero, or non-numeric capacity when creating an event.
- Empty or excessively long title/description.
- Event date in the past when creating an event.
- Two events created with overlapping date/time for organizer's own events —
  don't silently allow it; surface it and let the organizer confirm they
  still want to create it.
- Wrong/missing organizer password when trying to reach the organizer view.
- Basic XSS/injection attempts in title, description, or attendee name
  fields.

## Acceptance criteria (what "done" means)
- A fresh clone + the app's own README instructions is enough to run the
  app locally with no other context.
- Requirements 1-3 work end to end; requirement 4 works with at least the
  password gate + attendee list (CSV export is a stretch but attempted).
- Full-event and duplicate-email cases are rejected with clear messages, not
  silent failures or crashes.
- Invalid inputs (bad email, negative capacity, empty title) never crash the
  app or corrupt stored data.
- SECURITY_CHECK.md, PROMPT_LOG.md, VERIFICATION_NOTE.md, and BRIEF.md all
  exist in solution/ and are honest (documented mistakes/findings expected,
  not a "no issues found" report).

Ask me any clarifying questions before you start generating code — do not
assume answers to open points.
```

## Decisions locked in before coding started

These were resolved with the product owner before implementation, closing the
open points the prompt above deliberately left for confirmation:

| Decision | Choice |
|---|---|
| Backend stack | Node.js + Express |
| Frontend | Vanilla HTML/CSS/JS, no framework |
| Persistence | SQLite (file-based, `better-sqlite3`) |
| Organizer gating | Single shared password (`ORGANIZER_PASSWORD` env var) + session cookie |
| Attendee auth | None — name + email only, no accounts |
| Cross-origin access | Disabled — API only callable from the app's own frontend |
