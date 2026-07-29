# Prompt Log

> Record **every** prompt sent to the AI, in order, unedited. Add a one-line note on what you did with the response (accepted / modified / rejected). Exported chat links or screenshots may be attached instead, but the accept/modify/reject notes are still required.

## Tool & Workflow Note

**Tool used:** Claude Code (Sonnet 5), VSCode extension
**Mode(s) used:** Plan mode (read-only exploration + plan drafting), then agent mode (file writes + shell execution) for the build
**Notable limitations or surprises:** Plan mode blocked all non-read-only actions (including `ls`/`cat` outside Read/Bash-readonly), which forced an explicit clarification step (AskUserQuestion) before any code was written — a good forcing function, not a limitation per se. Two real surprises: (1) by the time I finished planning and checked in, `solution.py` and `pending.txt` already existed in the working tree (visible in `git status` from the very start of the session) — they were not something I generated in this conversation, so I had to verify their contents/correctness rather than assume they matched the plan; (2) that verification paid off — stress-testing with a synthetic UTF-8-BOM CSV revealed the script was silently misclassifying every row as invalid when a BOM was present (a realistic Excel-export artifact), which I then fixed (`encoding="utf-8"` → `"utf-8-sig"`). See `VERIFICATION_NOTE.md` for details.

## Deliverables: README called for → What I delivered

**`solution.py` (or your language of choice) — the final working code, runnable from the command line**
→ My `solution.py` reads the CSV, prints counts per status, and writes `pending.txt`. Handles missing name/email (→ `invalid`), missing status (→ `unknown`), whitespace/case variation, extra columns, blank lines, and missing input files. Fixed one real bug found during testing: it wasn't handling a UTF-8 BOM (common in Excel exports), which silently misclassified every row as invalid — fixed via `encoding="utf-8-sig"`.

**`PROMPT_LOG.md` — every prompt sent to the AI, in order; includes a Tool & Workflow Note**
→ This file: every prompt from this session, in order and unedited, each with an accepted/modified/rejected outcome, plus the Tool & Workflow Note above (tool, modes, and the two real surprises encountered).

**`VERIFICATION_NOTE.md` — 5–8 lines: what the AI got wrong or you had to correct, and how you verified correctness**
→ Documents the UTF-8 BOM bug: how it was found (stress-testing with synthetic edge-case CSVs, not just the sample file), how it was fixed, and how the final result was cross-checked against a manual tally of `data/engineers.csv`.

---

### Prompt 1
**Mode:** agent (plan mode)
```
this repo is a collection of 5 tests to asses the use of AI for coding.

currently we are gonna work in this folder tier-1-warmup 

Your job is to read the @tier-1-warmup/README.md file, understand the test it is giving and prepare a plan to present all the deliverable its asking for.

You will only act with the folders and files inside tier-1-warmup and the templates folder above it, do not go into other folders since they are other unrelevant tests.

Ask any questions that you need to comple the task.
```
**Outcome:** accepted — read README.md, data/engineers.csv, and templates/*.md, then asked two clarifying questions (prompt log source, language choice) before drafting the plan.

### Prompt 2
**Mode:** agent (plan mode — AskUserQuestion response)
```
"For PROMPT_LOG.md, since Claude Code is the AI tool being used for this exercise, should I populate it with the actual prompts from this session (this conversation, meta-style) as the record?"="Use this conversation (Recommended)", "Language for solution.py — README says Python or equivalent?"="Python (Recommended)"
```
**Outcome:** accepted — used these answers to finalize the plan (Python solution, meta prompt log from this session) and called ExitPlanMode.

### Prompt 3
**Mode:** agent (plan approved, exited plan mode)
```
Continue from where you left off.
```
**Outcome:** accepted — set up TodoWrite tracking and began implementation. 

With a fix along the way — checked directory state, found `solution.py`/`pending.txt` already present but `PROMPT_LOG.md`/`VERIFICATION_NOTE.md` missing. Ran the script against the sample CSV (counts matched a manual tally) and against several synthetic edge-case CSVs; the BOM test uncovered a real silent-failure bug, which I fixed and re-verified before writing `PROMPT_LOG.md` and `VERIFICATION_NOTE.md`.

### Prompt 4
**Mode:** agent
```
rewrite your last summary  (and make sure its also in the PROMPT_LOG.md) in a comparison format, for example:
README called for → What I delivered:
for example:
`solution.py` (or your language of choice) — the final working code, runnable from the command line
- My solution.py reads the CSV, prints counts per status, writes pending.txt. Handles missing name/email (→ invalid), missing status (→ unknown), whitespace/case variation, extra columns, blank lines, and missing input files. Fixed one real bug found during testing: it wasn't handling a UTF-8 BOM (common in Excel exports), which silently misclassified every row as invalid — fixed via encoding="utf-8-sig".
```
**Outcome:** accepted — added a "Deliverables: README called for → What I delivered" comparison section to this file and restated the end-of-turn summary in the same format.
