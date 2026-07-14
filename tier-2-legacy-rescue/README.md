# Tier 2 — Legacy rescue

**Time box:** 1–2 hours · **Points:** 100

## Scenario

You have inherited [`report_generator.py`](report_generator.py), an unmaintained script that generates a weekly training-compliance report. It "mostly works," but users report **wrong numbers and occasional crashes**. There are no tests and no documentation. The original author has left the company.

A sample input file is provided at [`data/sample_input.csv`](data/sample_input.csv).

## Your task

1. **Understand** — use an AI assistant to analyze the script. Produce a short `ANALYSIS.md` (10–20 lines) describing what it does, its inputs/outputs, and its structure.
2. **Find the bugs** — the script contains **4 planted defects** (logic, data handling, and robustness). Identify at least 3. Document each in `BUGS.md`: symptom, root cause, fix.
3. **Test** — write automated tests (`pytest` or `unittest`) in `test_report_generator.py` that **fail on the original code** for each bug found and **pass after your fix**. Minimum 5 test cases.
4. **Refactor** — deliver a corrected, readable `report_generator_fixed.py`: type hints, docstrings, no bare excepts, no global mutable state. Behavior (aside from bug fixes) must be preserved.

## Constraints

- AI assistance is expected and required — but **every bug you report must be reproduced by you** (a failing test or a demonstrated run), not just asserted by the AI. AI-reported "bugs" that don't exist count against you.
- Keep the CLI interface unchanged: `python report_generator_fixed.py <input.csv> <output.txt>`

## Deliverables

Place in this folder:

- `ANALYSIS.md` · `BUGS.md` · `test_report_generator.py` · `report_generator_fixed.py`
- `PROMPT_LOG.md` · `VERIFICATION_NOTE.md` (templates in [`../templates/`](../templates/))

Do **not** modify the original `report_generator.py` — the tests must be runnable against it to demonstrate the failures.

## Rubric (100 pts)

| Criterion | Pts | Exceeds | Meets | Below |
|---|---|---|---|---|
| Bug identification | 30 | All 4 found, root causes correct, no false positives | 3 found with correct root causes, or 4 with one false positive | ≤2 found, or multiple AI-hallucinated bugs reported |
| Tests | 25 | Failing-then-passing tests per bug + edge cases beyond the planted ones | ≥5 meaningful tests covering the found bugs | Tests trivial, don't target the bugs, or don't run |
| Refactor quality | 20 | Clean structure, typed, documented, behavior preserved | Improved but uneven | Behavior changed or quality unchanged |
| Analysis accuracy | 10 | Accurate, concise, includes data assumptions | Mostly accurate | Vague or AI boilerplate with errors |
| Prompt log & verification note | 15 | Shows iterative strategy: decomposition, follow-ups, cross-checking AI claims | Complete log, some iteration visible | Missing, incomplete, or single mega-prompt |
