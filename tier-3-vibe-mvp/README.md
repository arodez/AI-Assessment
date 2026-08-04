# Tier 3 — MVP from Scratch (Vibe Coding)

**Time box:** 2–3 hours · **Points:** 100

## Scenario

The communities team needs an MVP of the **Community Events Hub**: a mini-app to publish internal events (study groups, AMAs, workshops) and let people sign up. Nothing exists yet — no repo, no design, no backend. You must build it **from scratch, driving the AI with natural language** (vibe coding), using the tool of your choice: Replit, Claude, Cursor, Windsurf, etc.

The goal is to prove you can **specify, iterate, verify, and secure** an AI-generated product — the whole track in a single workflow.

## Functional requirements (the MVP)

1. **Create event** — title, date, description, and maximum capacity.
2. **Sign-up (RSVP)** — with validation: valid email, no duplicates per event, and a clear rejection when the event is full.
3. **Public list** — upcoming events sorted by date, showing available spots.
4. **Organizer view** — attendee list per event, exportable (CSV or copy).

Simple persistence (in-memory is fine for the MVP if documented as a limitation; file/SQLite is a plus). Free choice of stack.

## Process requirements (this is what gets graded)

### 0. Create a new folder called — `solution`
This will be the mvp app folder meaning all deliverables will put inside it

### 1. Product brief first — `BRIEF.md`
**Before generating a single line of code**, write your complete initial prompt: what is being built, for whom, requirements, technical constraints, expected edge cases, and acceptance criteria. 


### 2. Security pass before "sharing" — `SECURITY_CHECK.md`
Apply the vibe-coding course checklist before considering the MVP deliverable:
- No secrets/API keys in the code.
- Input validation (what happens with a malformed email, a negative capacity, an empty title?).
- No data exposure: can an attendee see everyone else's emails? Should they?
Document what you checked, what you found, and what you fixed.

### 3. Verification — `VERIFICATION_NOTE.md`
Test and document at least these 3 flows: (a) successful sign-up, (b) rejection when full, (c) rejection of a duplicate email. Include at least one mistake the AI made and how you caught it.

## Deliverables

- The MVP code (repo, zip, or Replit link) running, with startup instructions in its own `README.md`.
- `BRIEF.md` · `PROMPT_LOG.md` · `SECURITY_CHECK.md` · `VERIFICATION_NOTE.md` (templates in [`../templates/`](../templates/)).
- **Organizer dashboard** available at `/dashboard`, showing attendees per event and offering CSV export.


## Rubric (100 pts)

| Criterion | Pts | What "Meets" looks like |
|---|---|---|
| Product brief (initial prompt) | 20 | See prompt rubric below — the brief covers context, requirements, constraints, and acceptance criteria |
| Working MVP | 25 | Requirements 1–3 work end to end; 4 at least partially; starts from the README alone |
| Iteration | 15 | ≥3 real correction cycles visible in the prompt log, with clear cause and effect |
| Validation & data | 15 | Full-event and duplicate-email cases rejected correctly; invalid inputs don't break the app |
| Security pass | 10 | Checklist applied honestly; no secrets; at least one real finding fixed |
| Verification | 15 | The 3 flows tested and documented; at least one AI mistake caught with evidence |

### Prompt rubric (applies to the brief and the prompt log)

Each relevant prompt is evaluated across 5 dimensions (0–2 pts each on the brief):

| Dimension | 2 pts | 0 pts |
|---|---|---|
| **Context** | Explains the what and the for whom | Assumes the AI will guess |
| **Specificity** | Concrete, measurable requirements | "Make me an events app" |
| **Constraints** | Stack, limits, what NOT to do | No constraints at all |
| **Edge cases** | Anticipates errors and invalid data | Happy path only |
| **Acceptance criteria** | Defines a verifiable "done" | No definition of success |

**Pass:** ≥70 total. **Note:** a flawless MVP with an empty or reconstructed prompt log fails the iteration criterion — the process is the exam.
