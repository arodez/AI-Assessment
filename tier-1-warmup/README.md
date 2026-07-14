# Tier 1 — Warm-up script

**Time box:** 25 minutes · **Points:** 30

## Task

Using any AI coding assistant, build a small CLI or script:

> A tool that reads a CSV of engineers (`name,email,course_status`) and outputs:
> **(a)** the count per status, and
> **(b)** a list of emails with status `"pending"`, written to `pending.txt`.

A sample input file is provided at [`data/engineers.csv`](data/engineers.csv).

## Deliverables

Place in this folder:

- `solution.py` (or your language of choice) — the final working code
- `PROMPT_LOG.md` — every prompt sent to the AI, in order
- `VERIFICATION_NOTE.md` — 5–8 lines: what the AI got wrong or you had to correct, and how you verified correctness

Templates for the last two are in [`../templates/`](../templates/).

## Rubric (30 pts)

| Criterion | Exceeds (full pts) | Meets (~70%) | Below |
|---|---|---|---|
| Working code (10) | Handles edge cases (empty file, missing columns) | Works on happy path | Doesn't run |
| Prompt quality (10) | Clear context, constraints, examples, iterative refinement | Adequate but vague in places | "Do it for me" one-liners only |
| Verification (10) | Wrote/ran tests or manual checks; caught at least one AI error | Ran the code, spot-checked output | Accepted output blindly |
