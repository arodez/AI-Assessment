# Tier 1 — Warm-up Script

**Time box:** 25 minutes · **Points:** 30

## Task

Using any AI coding assistant, build a small CLI or script:

> A tool that reads a CSV of engineers (`name,email,course_status`) and outputs:
> **(a)** the count per status, and
> **(b)** a list of emails with status `"pending"`, written to `pending.txt`.

A sample input file is provided at [`data/engineers.csv`](data/engineers.csv).

> **Note:** The input file may contain imperfect rows. Your script should handle them gracefully.

Run your script from the command line: `python solution.py` (or equivalent for your language).

## Deliverables

Create a folder called `solution` and place in that folder:

- `solution.py` (or your language of choice) — the final working code, runnable from the command line
- `PROMPT_LOG.md` — every prompt sent to the AI, in order; includes a **Tool & Workflow Note** (which tool, which mode(s), any surprises or limitations encountered)
- `VERIFICATION_NOTE.md` — 5–8 lines: what the AI got wrong or you had to correct, and how you verified correctness

Templates for the last two are in [`../templates/`](../templates/).

## Rubric (30 pts)

| Criterion | Exceeds (10 pts) | Meets (7 pts) | Below (≤ 4 pts) |
|---|---|---|---|
| Working code (10) | Handles edge cases (empty rows, missing columns) | Works on happy path only | Doesn't run or produces wrong output |
| Prompt quality (10) | Clear context, constraints, examples, iterative refinement | Adequate but vague in places | "Do it for me" one-liners only |
| Verification (10) | Wrote/ran tests or manual checks; caught at least one AI error | Ran the code, spot-checked output | Accepted output blindly |
