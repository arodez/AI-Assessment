# Tier 3 — MVP Planning (Vibe Coding)

**Time box:** 2–3 hours · **Points:** 100

## Scenario

The communities team needs an MVP of the **Community Events Hub**: a mini-app to publish internal events (study groups, AMAs, workshops) and let people sign up. Nothing exists yet — no repo, no design, no backend. Your job is **not** to build it. Your job is to produce the **plan** someone (you, in a later session, or another engineer) would need to build it **from scratch, driving the AI with natural language** (vibe coding), using the tool of your choice: Replit, Claude, Cursor, Windsurf, etc.

The goal is to prove you can **specify and plan** an AI-driven build before any code exists: turn a rough scenario into a complete, actionable plan — requirements, technical approach, edge cases, security considerations, and how you'd verify it — solid enough that a build session could start from it with no further clarification.

**No app code is required or expected for this exercise.** Every deliverable is a markdown document.

## Functional requirements (the MVP)

These define what the eventual MVP must do — your plan needs to address how each one gets built, not implement it:

1. **Create event** — title, date, description, and maximum capacity.
2. **Sign-up (RSVP)** — with validation: valid email, no duplicates per event, and a clear rejection when the event is full.
3. **Public list** — upcoming events sorted by date, showing available spots.
4. **Organizer view** — attendee list per event, exportable (CSV or copy).

Simple persistence (in-memory is fine for the MVP if documented as a limitation; file/SQLite is a plus). Free choice of stack — your plan should state and justify the choice.

## Process requirements (this is what gets graded)

### 0. Create a new folder called — `solution`
This will hold all deliverables for this exercise. It contains only markdown documents — no app code.

### 1. Product brief first — `BRIEF.md`
**Before writing the plan**, write your complete initial prompt: what is being built, for whom, requirements, technical constraints, expected edge cases, and acceptance criteria.

### 2. The delivery plan — `PLAN.md`
The core deliverable. This is the markdown plan/context you'd hand to an AI (or a teammate) to actually deliver the MVP. It should cover:
- **Architecture & stack** — chosen stack and why, persistence approach and its limitations.
- **Data model** — the shape of events and sign-ups, and how the constraints (capacity, uniqueness) are represented.
- **Flows** — how each of the 4 functional requirements gets implemented, screen by screen or endpoint by endpoint.
- **Edge cases** — malformed email, negative/zero capacity, empty title, full event, duplicate sign-up — and how each is meant to be handled.
- **Out of scope / limitations** — what the MVP deliberately won't do, and known trade-offs (e.g., in-memory persistence).
- **Task breakdown** — an ordered list of build steps an AI session could follow.

### 3. Security pass on the plan — `SECURITY_CHECK.md`
Apply the vibe-coding course checklist to the **planned design**, not to running code:
- What secrets/API keys would the app need, and how does the plan keep them out of the codebase?
- What validation does the plan specify for a malformed email, a negative capacity, an empty title?
- What data exposure risks exist in the planned data model or API (e.g., can an attendee see everyone else's emails)? Should they? How does the plan prevent it?
Document what you checked, what risks you found, and how the plan mitigates each one.

### 4. Verification plan — `VERIFICATION_NOTE.md`
Define the test plan for at least these 3 flows: (a) successful sign-up, (b) rejection when full, (c) rejection of a duplicate email. For each, specify the inputs, the expected result, and how it would be confirmed once built (manual test, unit test, etc.) — this documents *how* verification would happen, not actual run results, since nothing is built yet. Include at least one moment where the AI's first draft of the plan was wrong or incomplete, and how you caught and corrected it.

## Deliverables

- `PLAN.md` — the delivery plan/context that would be used to build the MVP (no running app required).
- `BRIEF.md` · `PROMPT_LOG.md` · `SECURITY_CHECK.md` · `VERIFICATION_NOTE.md` (templates in [`../templates/`](../templates/)).

## Rubric (100 pts)

| Criterion | Pts | What "Meets" looks like |
|---|---|---|
| Product brief (initial prompt) | 20 | See prompt rubric below — the brief covers context, requirements, constraints, and acceptance criteria |
| Delivery plan | 25 | `PLAN.md` is complete and actionable: covers architecture/stack, data model, all 4 functional requirements, and edge cases — a build session could start from it with no further clarification |
| Iteration | 15 | ≥3 real correction cycles visible in the prompt log while developing the plan, with clear cause and effect |
| Validation & data design | 15 | The plan clearly specifies how full-event and duplicate-email cases are rejected and how invalid inputs are handled — judged on completeness and correctness of the design |
| Security pass | 10 | Checklist applied honestly to the planned design; realistic risks identified with concrete, specific mitigations |
| Verification plan | 15 | The 3 flows have a clear test plan with inputs and expected results; at least one planning mistake caught with evidence |

### Prompt rubric (applies to the brief and the prompt log)

Each relevant prompt is evaluated across 5 dimensions (0–2 pts each on the brief):

| Dimension | 2 pts | 0 pts |
|---|---|---|
| **Context** | Explains the what and the for whom | Assumes the AI will guess |
| **Specificity** | Concrete, measurable requirements | "Make me an events app" |
| **Constraints** | Stack, limits, what NOT to do | No constraints at all |
| **Edge cases** | Anticipates errors and invalid data | Happy path only |
| **Acceptance criteria** | Defines a verifiable "done" | No definition of success |

**Pass:** ≥70 total. **Note:** a flawless-looking plan with an empty or reconstructed prompt log fails the iteration criterion — the process is the exam.
