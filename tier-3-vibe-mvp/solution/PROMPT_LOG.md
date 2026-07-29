# Prompt Log

## Tool & Workflow Note

**Tool used:** Claude Code (Sonnet 5)
**Mode(s) used:** agent (plan mode for the design pass, then agentic build/edit/bash in the main session)
**Notable limitations or surprises:** Claude Code is a single long-running
agentic session rather than a turn-by-turn chat — most "correction cycles"
below came from the agent's own build-and-verify loop (running the real app
in a headless browser and catching bugs from the actual behavior) rather than
a human re-prompting after every response. The two most notable surprises:
`better-sqlite3`'s prebuilt binary didn't support the installed Node version
and had to be upgraded before anything would run at all, and a self-inflicted
double-escaping bug that only became visible once the app was actually driven
in a browser rather than just read as code.

---

### Prompt 1 — initial draft brief
**Mode:** chat (refinement pass, no code yet)
```
this repo is a collection of 5 tests to asses the use of AI for coding.

currently we are gonna work in this folder tier-3-vibe-mvp
[... full draft: MVP scope (create/RSVP/public list/organizer view),
instruction to read tier-3-vibe-mvp/README.md, edge-case pointers
(sanitized inputs, correct login per view, date/time overlap, duplicate
emails), and the 3-flow verification requirement ...]
```
**Outcome:** modified — the draft was missing explicit stack/persistence/
gating decisions, the SECURITY_CHECK.md and PROMPT_LOG.md deliverables, and
concrete acceptance criteria. Read `tier-3-vibe-mvp/README.md` and
`templates/*.md`, then asked 3 clarifying questions (stack, organizer gating
mechanism, persistence) via structured Q&A before finalizing the brief.

### Prompt 2 — clarifying answers
**Mode:** chat
```
"What tech stack should the prompt lock in for the MVP?" → Node/Express + vanilla HTML/JS
"How should the organizer view be 'gated'?" → Single shared organizer password
"Persistence approach?" → SQLite file-based
```
**Outcome:** accepted — folded directly into the refined brief as a locked-in
decisions table.

### Prompt 3 — finalized brief (pasted back verbatim by the user)
**Mode:** chat → plan mode
```
This repo is a collection of 5 tests to assess the use of AI for coding. We are
working ONLY inside tier-3-vibe-mvp/ and the shared ../templates/ folder —
[... full finalized brief: context, deliverables & structure, functional
requirements 1-4, constraints (Node/Express, SQLite, no attendee accounts, no
CORS), edge cases, acceptance criteria ...]
```
**Outcome:** accepted as the seed for `BRIEF.md`. Entered plan mode to design
the implementation before writing code.

### Prompt 4 — plan rejection
**Mode:** plan mode
```
curl access is of scope right now, make sure requests are secured to only in app calls
```
**Outcome:** modified — the first plan's verification section proposed
testing routes with `curl`. Revised the plan to (a) add an explicit
no-CORS/same-origin constraint to the security posture and (b) switch
verification to browser-driven testing only, no direct API scripting from
outside the app. Re-submitted the plan; approved on the second pass.

### Prompt 5 (internal) — dependency install failure
**Mode:** agent (bash)
```
npm install → better-sqlite3@11.3.0 native build fails against Node v26
(node-gyp/V8 API mismatch, "'Value' is deprecated" compiler errors)
```
**Outcome:** modified — bumped `better-sqlite3` to `^13.0.2` in
`package.json`, reinstalled clean; build succeeded with 0 vulnerabilities.

### Prompt 6 (internal) — browser-driven verification surfaces UI bug
**Mode:** agent (Playwright script driving the running app)
```
Signup flow returns 200 and the correct success message body, but
waitForSelector('.message.success') times out — the message is never
actually observable in the rendered page.
```
**Outcome:** modified — found that the signup handler called `loadEvents()`
synchronously right after setting the success message, wiping the whole
events container in the same tick before the browser could paint it. Fixed
by deferring the refresh with `setTimeout(loadEvents, 1500)`. Re-ran the
verification script; the message is now visible in the screenshot.

### Prompt 7 (internal) — XSS test surfaces a display bug
**Mode:** agent (Playwright script + screenshot review)
```
Titles containing `<script>`/`<img onerror>` payloads render as literal
"&lt;script&gt;..." text instead of the actual typed characters, even though
the script never executes.
```
**Outcome:** modified — root cause was double protection: server-side
`escapeHtml()` on write, plus client-side `textContent` rendering (already
XSS-safe on its own). Removed the redundant server-side escaping from
`validation.js`, `routes/events.js`, and `routes/signup.js`. Re-ran the same
payloads: still doesn't execute, now displays as plain typed text.
