# Prompt Log

> Record **every** prompt sent to the AI, in order, unedited. Add a one-line note on what you did with the response (accepted / modified / rejected).

## Tool & Workflow Note

**Tool used:** Claude (claude.ai, chat interface with code execution)
**Mode(s) used:** chat (agentic — Claude reads/writes files directly via tools in this session)
**Notable limitations or surprises:**
- No network egress in the code execution sandbox — `npm install` failed with a 403 `host_not_allowed` error, forcing a pivot from the planned Express + `better-sqlite3` + EJS stack to a zero-dependency build using Node's built-in `http` and `node:sqlite` modules (see Prompt 3).
- Backgrounded server processes do not persist between separate tool calls — each call is its own isolated shell lifecycle. Solved by running server-start + all verification curls inside a single tool call per test (see Prompt 4).
- Concurrent curl calls without a `--max-time` guard could hang an entire tool call rather than failing individual requests — a sandbox/tooling interaction, not an app bug (see Prompt 5).
- Caught myself writing a security-doc claim ("`.env` is gitignored") before the referenced file actually existed — fixed by creating it first rather than leaving the documentation aspirational (see Prompt 7).
- None of these were "the AI refused" cases — all were environment constraints discovered empirically and adapted to, then documented rather than hidden.

---

### Prompt 1
**Mode:** chat
```
Read the whole README.md file and ask the necessary questions to be able to have
all the information needed to plan for this MVP. Do not write or start anything
until we have a plan that is approved.

Take into consideration possible Edge Cases, sanitized data (inputs) or general
data to avoid conflicts, and the verification of at least the 3 flows mentioned
in the README.md

Generate the PROMPT_LOG.md and the VERIFICATION_NOTE.md
```
**Outcome:** accepted — AI asked 8 clarifying questions across two rounds (stack, frontend approach, organizer auth, data exposure, validation rules, duplicate-email matching, token setup, CSV export) before producing a plan. Plan was reviewed and approved before any code was written.

### Prompt 2
**Mode:** chat
```
this plan is approved
```
**Outcome:** accepted — triggered AI to write BRIEF.md (the graded product brief) reflecting all decisions made during the Q&A rounds: stack (Node/Express/SQLite/EJS), organizer token auth, validation rules, edge cases, and acceptance criteria. No code written yet.

### Prompt 3
**Mode:** chat (agentic — AI ran `npm install` itself to scaffold the app)
```
(no new user prompt — AI proceeded to scaffold the app per the approved BRIEF.md plan: Express + better-sqlite3 + EJS)
```
**Outcome:** rejected/modified — `npm install` failed with a 403 `host_not_allowed` error; this sandbox has no network egress at all, confirmed via a direct curl to the npm registry. Neither `better-sqlite3`, `express`, nor `ejs` are pre-cached in the environment. This is exactly the kind of "AI mistake" the assignment wants documented: the plan assumed a capability (installing npm packages) that wasn't actually available in this execution environment, and it wasn't caught until actually trying to install.

**Correction:** switched to a **zero-dependency** implementation:
- `node:sqlite` (Node's built-in experimental SQLite module, confirmed working on Node v22.22.2) instead of `better-sqlite3`
- Node's built-in `http` module + a small hand-rolled router instead of Express
- A tiny hand-written HTML template helper instead of EJS

This is a deviation from BRIEF.md's stated stack, documented here and in the app's own README.md. The tradeoff: no external dependencies means `npm install` isn't even needed for a grader to run this, which is arguably more robust for grading purposes — but `node:sqlite` is still an experimental Node API (logs an ExperimentalWarning) and requires Node ≥22.5. This will be flagged clearly as a known limitation.

### Prompt 4
**Mode:** chat
```
let's divide the plan from the first response in small deliverables so the
token limitation doesnt affect the creation of new files of progression in
this MVP. Proceed with the plan but in small increments
```
**Outcome:** accepted — restructured remaining work into 8 checkpointed increments (3–8: smoke test, required-flow verification, edge cases, security doc, README, final packaging), each stopping for review before continuing. Immediately hit and solved a real environment issue: backgrounded server processes do NOT persist between separate bash_tool calls (each call is an isolated shell lifecycle) — confirmed via a failed curl after backgrounding in one call vs. checking in the next. Fixed by running server-start + all curl tests within a single bash_tool call per verification increment.

**Increment 3 (smoke test all routes):** all 9 routes tested (homepage, create form, create submit, list-reflects-new-event, event detail, organizer login unauthed, organizer wrong token, organizer correct token, 404) — all returned expected status codes. Follow-up check confirmed the organizer gate is real, not cosmetic: wrong/missing token on `/organizer` renders the login page body (not dashboard content); wrong/missing token on the deeper `/organizer/events/:id` and `/export.csv` routes returns a hard 401 with no data in the body. **Increment 3 complete, verified, stopped for review.**

### Prompt 5
**Mode:** chat
```
proceed
```
**Outcome:** accepted — ran Increment 4 (the 3 required flows). First attempt at Flow C (duplicate email) was invalid evidence: it ran against an event already filled by Flow B, so the 409 could have come from either the "full" or "duplicate" check — caught this ambiguity before treating it as valid verification, and re-ran Flow C in isolation against a fresh event with plenty of spare capacity to confirm the 409 was genuinely the duplicate-email check.

Went further than strictly required and stress-tested concurrent duplicate RSVPs (multiple simultaneous requests, same email, capacity=1) to check whether the DB-level UNIQUE constraint actually prevents double sign-ups under a race, not just the app-level pre-check (which can race). Hit real friction: an early attempt without per-request `curl --max-time` guards caused the bash_tool call to hang and time out — a tooling/sandbox interaction issue, not an app bug, confirmed by checking for stray processes afterward (none found). Recovered by always wrapping concurrent curls with `--max-time`. With that fix, both a 2-concurrent and a 5-concurrent test completed cleanly: in every run, exactly one request succeeded and all others were correctly rejected as duplicates — zero double sign-ups even under concurrency.

All 3 required flows confirmed with clean, isolated evidence — see VERIFICATION_NOTE.md for the full transcripts and results.

### Prompt 6
**Mode:** chat
```
proceed
```
**Outcome:** accepted — ran Increment 5 (edge case sweep), 20 total checks across event creation, RSVP, security:

Event creation: negative capacity, zero capacity, decimal capacity, non-numeric capacity, empty title, whitespace-only title, past date — all correctly rejected with 400 + clear error messages.

RSVP: malformed email (no @, trailing @, leading @), empty email, empty name, RSVP to nonexistent event ID, GET nonexistent event detail page, non-numeric event ID in URL — all correctly rejected (400 or 404 as appropriate).

Security: XSS payloads in event title and RSVP name were stored literally and rendered HTML-escaped (not executed) on both the public list and the organizer attendee view; SQL injection attempt in event title was treated as a literal parameterized value — the events table remained intact and the malicious string appeared as harmless visible text, not as an executed statement; SQL injection attempt in RSVP email was actually blocked earlier by the email-format validator, before it ever reached the database layer. Also explicitly re-confirmed the BRIEF's "no attendee data on public routes" requirement by seeding an attendee with distinctive name/email values and grepping both public pages for any trace — none found.

No bugs found in this pass — noting that honestly rather than manufacturing a finding, since the validation and escaping layers written in Increments 2–3 were built with these exact cases in mind from the start.

### Prompt 7
**Mode:** chat
```
Proceed
```
**Outcome:** accepted — wrote SECURITY_CHECK.md, but only after cross-checking each claim against files that actually exist. Caught a gap while writing it: the draft referenced ".env is listed in .gitignore" as already true, but no .gitignore file had actually been created yet in Increments 2–3 — the claim would have been false documentation. Fixed by creating .gitignore (node_modules/, .env, data.sqlite, *.log) and .env.example (documents ORGANIZER_TOKEN and PORT without committing a real secret) before finalizing the security doc, so every statement in SECURITY_CHECK.md is backed by something real in the repo, not aspirational.

### Prompt 8
**Mode:** chat
```
proceed
```
**Outcome:** accepted — wrote the app's own README.md (startup instructions, project structure, known limitations, and the "why no dependencies" explanation), then verified it against a genuinely fresh run: deleted data.sqlite and .env, ran only `node server.js` exactly as the README instructs, confirmed the homepage returned 200 and the boot log matched what the README shows verbatim. Also finalized this file's "Tool & Workflow Note" section at the top, listing the real environment constraints hit during the build (no network egress, backgrounded processes not persisting across tool calls, unguarded concurrent curls hanging a tool call, and one documentation-before-reality gap) rather than leaving it as a placeholder.

### Prompt 9
**Mode:** chat
```
proceed
```
**Outcome:** accepted — final pass (Increment 8). Found and removed a stray data.sqlite file left over from testing, which shouldn't ship as part of the deliverable (it's meant to be auto-generated on first run, not handed over pre-populated with test data). Re-ran a full end-to-end smoke test against the cleaned folder (homepage → create event → RSVP → event detail → organizer login → CSV export, all 200/302 as expected) to confirm the cleanup didn't break anything, then deleted the resulting test DB again so the final deliverable starts genuinely empty. Cross-checked README.md's documented project structure against the actual filesystem (all 14 listed files confirmed present) and confirmed BRIEF.md's Stack section still accurately reflects the zero-dependency pivot rather than the original Express/EJS plan. No further issues found — packaging complete.
