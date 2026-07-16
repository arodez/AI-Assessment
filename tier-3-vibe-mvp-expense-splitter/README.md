# Tier 3 (Variant B) — Expense Splitter (Vibe Coding)

**Time box:** 2–3 hours · **Points:** 100

> This is an alternative to [Variant A — Community Events Hub](../tier-3-vibe-mvp/). Candidates complete **one** variant, assigned by the evaluator. Both use the same process requirements and prompt rubric.

## Scenario

Build a web application that helps friends split expenses during a trip. Nothing exists yet — no repo, no design. You must build it **from scratch, driving the AI with natural language** (vibe coding), using the tool of your choice: Replit, Claude, ChatGPT, Cursor, Windsurf, v0, etc.

The goal is NOT to prove you can code it by hand. It's to prove you can **decompose requirements, specify, iterate, and verify** an AI-generated product.

## Functional requirements (the MVP)

1. **Add participants** to the trip.
2. **Add expenses** — description, amount, and **who paid**.
3. **Split equally** among participants.
4. **Show balances** — how much each person is up or down overall.
5. **Display who owes whom** — a settlement view (e.g., "Carla → Ana: $110").
6. **Persist data locally** — localStorage or a simple backend; refreshing the page must not lose the trip.

## Bonus (up to +10 pts, not required to pass)

- Unequal splits (percentages, exact amounts, or per-expense participant selection)
- Delete/edit expenses (balances must recalculate correctly)
- Export to JSON

## What this exercise tests

Requirement decomposition · state management · basic UI · AI-assisted implementation — and above all, whether you **verify the money math** instead of trusting it.

## Process requirements (this is what gets graded)

### 1. Product brief first — `BRIEF.md`
**Before generating a single line of code**, write your complete initial prompt: what is being built, requirements, constraints, edge cases, and acceptance criteria. Graded with the 5-dimension prompt rubric. Money apps punish vague briefs: think about rounding, zero/negative amounts, and what happens when a participant is added *after* expenses exist — before the AI decides for you.

### 2. Documented iteration
At least **3 visible refinement cycles** in your `PROMPT_LOG.md`: what came out wrong or incomplete, what correction prompt you sent, and what changed.

### 3. Verification — `VERIFICATION_NOTE.md`
You MUST verify the settlement math by hand against at least one scenario of your own design (3+ participants, 3+ expenses, unequal payments) and document the hand calculation next to the app's output. Include at least one mistake the AI made and how you caught it.

### 4. Data integrity note — inside `VERIFICATION_NOTE.md`
Answer explicitly: what happens with (a) an amount of 0 or negative, (b) an amount like 100 split 3 ways (rounding — where does the extra cent go?), (c) deleting a participant who has paid expenses? "The app prevents it" and "the app allows it and here's why" are both acceptable — *undefined and untested* is not.

## Deliverables

- The app (repo, zip, or link) running, with startup instructions in its own `README.md`.
- `BRIEF.md` · `PROMPT_LOG.md` · `VERIFICATION_NOTE.md` (templates in [`../templates/`](../templates/)).

## Rubric (100 pts + 10 bonus)

| Criterion | Pts | What "Meets" looks like |
|---|---|---|
| Product brief (initial prompt) | 20 | Prompt rubric below — including at least 2 money-specific edge cases anticipated (rounding, invalid amounts, late participants) |
| Working MVP | 25 | Requirements 1–5 work end to end; persistence (6) survives a refresh; starts from the README alone |
| Settlement correctness | 15 | Balances AND who-owes-whom are correct on the evaluator's test scenario; sum of balances = 0 |
| Iteration | 15 | ≥3 real correction cycles visible in the prompt log, with clear cause and effect |
| Verification & data integrity | 15 | Hand-checked scenario documented; the 3 integrity questions answered and tested; at least one AI mistake caught with evidence |
| UI clarity | 10 | A stranger can add a trip's expenses and read who owes whom without instructions |
| **Bonus** | +10 | Unequal splits (+5), edit/delete with correct recalculation (+3), JSON export (+2) |

### Prompt rubric (applies to the brief and the prompt log)

Each dimension 0–2 pts on the brief:

| Dimension | 2 pts | 0 pts |
|---|---|---|
| **Context** | Explains the what and the for whom | Assumes the AI will guess |
| **Specificity** | Concrete, measurable requirements | "Make me an expense splitter" |
| **Constraints** | Stack, limits, what NOT to do | No constraints at all |
| **Edge cases** | Anticipates rounding, invalid amounts, membership changes | Happy path only |
| **Acceptance criteria** | Defines a verifiable "done" with numbers | No definition of success |

**Pass:** ≥70 (bonus points can lift a 65–69 across the line only if settlement correctness scored full marks). An empty or reconstructed prompt log fails the iteration criterion — the process is the exam.
