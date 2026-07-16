# Tier 3 (Vibe MVP) — Reference solution: optimal prompt sequence

**DO NOT DISTRIBUTE TO CANDIDATES.** This is the measuring stick for grading the brief and the prompt log. Candidates are not expected to write exactly this — their work is expected to cover the same elements.

---

## Prompt 1 — The optimal brief (what "Exceeds" looks like)

> I want to build an MVP called **Community Events Hub** so members of an internal engineering community can publish events (study groups, AMAs, workshops) and others can sign up.
>
> **Users:** organizers (create events, see attendees) and attendees (browse events, sign up). No login for the MVP: the organizer view lives on a separate `/admin` route.
>
> **Requirements:**
> 1. Create event: title (required, non-empty), date (must be in the future), description, max capacity (integer ≥ 1).
> 2. RSVP: name + email. Validate email format, reject duplicates per event, reject when the event is full with a clear message (not a generic error).
> 3. Public list: upcoming events sorted by date, showing "X of Y spots available." Past events don't appear.
> 4. Organizer view: attendees per event with a CSV export button.
>
> **Stack and constraints:** Python + Flask, single app, no external database — persistence in a JSON file. No frontend frameworks; Flask templates with minimal CSS. Don't invent features I didn't ask for (no auth, no real emails, no payments).
>
> **Edge cases it must handle without breaking:** malformed email, capacity 0 or negative at event creation, empty title, sign-up for a nonexistent event, two simultaneous sign-ups for the last spot (one being cleanly rejected is enough).
>
> **Acceptance criteria:** I can create an event with capacity 2, register 2 people, and the third attempt is rejected with a visible message; a repeated email on the same event is rejected; the exported CSV opens in Excel with the correct attendees.
>
> Start by showing me the file structure and the plan before generating the full code.

**Why it's optimal (against the 5-dimension rubric):** context ✓ (what and for whom), specificity ✓ (concrete validations), constraints ✓ (fixed stack, "don't invent features"), edge cases ✓ (explicit list), acceptance criteria ✓ (manually verifiable). The closing "show me the plan before the code" is the controlled-iteration habit from the AI-Assisted Coding course.

## Prompts 2–4 — Typical optimal iterations

**Correction iteration (example):**
> The full-event rejection doesn't work: I created an event with capacity 2, registered 3 people, and all 3 appear. Here is the sign-up function you generated: [paste code]. The count seems to happen before the validation. Fix only that function, don't regenerate the whole app, and tell me what you changed.

*(Optimal because: it reports symptom + reproduction, scopes the change — "only that function" — and asks for an explanation of the change. This is exactly what separates iterating from re-rolling the dice.)*

**Validation iteration:**
> Thought experiment: what happens today if I submit the RSVP form with the email "hi@" or empty? Review the validation code and list which invalid inputs are NOT covered yet, before changing anything.

*(Optimal because: it uses the AI to audit before modifying — directed verification, not blind trust.)*

**Security iteration (before delivering):**
> Before sharing this app: review the code and tell me (1) whether any sensitive data is exposed on public routes — in particular, are attendees' emails visible to other attendees?, (2) whether any inputs lack server-side validation, (3) whether anything is hardcoded that shouldn't be. Don't change anything yet, just list the findings.

## Expected security finding

The exercise statement contains a deliberate trap: the "public list" plus RSVP naturally lead the AI to display **attendees' emails on the public view**. A strong candidate catches this in their security pass (emails should only be visible on `/admin`). If `SECURITY_CHECK.md` doesn't mention personal-data exposure, the security criterion cannot score above low "Meets."

## Evaluator acceptance checklist (15 min)

1. Start the app using only the candidate's README.
2. Create an event with capacity 2 → register 2 → the 3rd must be rejected with a clear message.
3. Register the same email twice → rejected.
4. Email "hi@" → rejected without a stack trace.
5. Create an event with capacity -1 or an empty title → rejected.
6. Are other attendees' emails visible on the public view? (should be NO, or justified).
7. Export the CSV and open it.
8. Cross-check the prompt log against the code: do the described iterations match what exists?

## Grading the brief with the prompt rubric

| Dimension | Minimum evidence for 2 pts |
|---|---|
| Context | Says what the app is and who uses it |
| Specificity | All 4 features with at least one concrete validation each |
| Constraints | Stack defined + at least one "don't do X" |
| Edge cases | ≥3 invalid cases anticipated before generating code |
| Acceptance criteria | At least one step-by-step verifiable scenario |

A brief scoring 8–10 = a candidate who internalized the prompting chapter. A brief scoring ≤4 ("make me an events app with Flask") = they didn't, even if the MVP works — modern AI can rescue a bad brief, which is exactly why the brief is graded as a separate artifact.
