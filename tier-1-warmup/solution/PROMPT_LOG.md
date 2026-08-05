# Tier 1 Warm Up — Solution Prompt Log

| Field      | Value                               |
| ---------- | ------------------------------------ |
| **Tool**   | Claude Code                         |
| **Repo**   | AI-Assessment / tier-1-warmup        |
| **Branch** | JavierCA_Solution_WarmUp             |

## Tool & Workflow Note

**Tool used:** Claude Code (Sonnet 5)
**Mode(s) used:** Plan mode (requirements gathering, clarifying questions, design review) → auto/accept-edits (implementation)
**Notable limitations or surprises:**
- Poetry and pytest were not pre-installed on the dev machine, and only Python 3.14.6 (very recently released) was available — this had to be discovered and handled during planning rather than assumed.
- The AI's first draft of the plan proposed a loose `python = "^3.11"` constraint in `pyproject.toml`; I corrected it during plan review to `^3.14` to match the interpreter actually installed and tested, rather than claiming broader compatibility that was never verified.
- Everything else (Poetry install via Homebrew, dependency resolution, full test suite, manual CLI run against the real sample data) worked on the first attempt with no further surprises.

---

## Prompt 1

> Let's create a Python CLI tool `solution.py` that takes the path to a CSV file containing engineers' data. The engineers' data has three columns: `name`, `email`, `course_status`. Note that all fields can be optional, and the CSV could contain badly formatted or empty rows. The tool should print (a) total engineers processed, (b) per-status counts, (c) the name of a written pending file, and write `pending-[TIMESTAMP].txt` (ISO datetime) listing emails with `pending` status. Include a `/tests` folder with CSV examples for happy path and edge cases (positive and negative) to validate the tool with pytest. Full implementation in `./solution`, packaged with `pyproject.toml`, dependency-managed with Poetry. Create a `GUIDE.md` covering usage, how to contribute (Gitflow, Python env setup/activate/deactivate, running/adding tests), and how to report an error.

### Metadata

| Field             | Value                    |
| ----------------- | ------------------------ |
| **Date/Time**     | 2026-08-04 (plan mode)    |
| **Model**         | Sonnet 5                 |
| **Mode**          | plan → auto/accept-edits |
| **Tags**          | csv-cli, pytest, poetry, edge-cases, plan-mode |

### Outcome

Accepted, with iterative refinement. Before any code was written, Claude Code entered plan mode: ran an Explore agent to check the local environment (confirmed Poetry/pytest were not installed, only Python 3.14.6 present; reviewed the deliberately messy sibling `tier-2-legacy-rescue/report_generator.py` as an anti-pattern *not* to imitate; confirmed the sample `data/engineers.csv` and its two known malformed rows), then asked 4 clarifying questions via AskUserQuestion before drafting a design:

1. Should rows with missing `name`/`email` still count toward totals? → **Yes, count them.**
2. What label for missing/blank `course_status`? → **`unknown`.**
3. Should status matching be case/whitespace-normalized? → **Yes, normalize.**
4. Poetry isn't installed — install it now, or just write config? → **Install it now** (via Homebrew).

A Plan agent then drafted a detailed implementation plan (module design, `pyproject.toml`, 11 test fixtures + test plan, `GUIDE.md` outline, execution order, verification commands). I reviewed the plan and **directly edited it** before approving: changed the `python` version constraint from `^3.11` to `^3.14` (to match the only interpreter actually available/tested), and changed where `PROMPT_LOG.md`/`VERIFICATION_NOTE.md` get copied from (the local `tier-1-warmup/` root copies instead of the monorepo `templates/` folder).

Implementation then proceeded exactly per the approved plan: `solution.py` ([solution.py](solution.py)), `pyproject.toml` ([pyproject.toml](pyproject.toml)), 11 fixture CSVs and `tests/test_solution.py` ([tests/](tests/)), `GUIDE.md` ([GUIDE.md](GUIDE.md)). Poetry was installed via `brew install poetry`, `poetry lock && poetry install` succeeded on the first try under Python 3.14.6, and `poetry run pytest -v` passed all 35 tests on the first full run. A manual run against the real `../data/engineers.csv` matched the hand-computed expected numbers exactly (10 total, 3 pending, 3 completed, 2 in_progress, 2 unknown; pending file contained exactly the 3 expected emails).

### Highlights

- Using `csv.DictReader`'s built-in `restval`/`restkey` behavior (rather than manual per-row `try/except` or index access) handled both known malformed-row shapes (missing trailing column, extra columns) and blank-line skipping for free, with no special-casing needed.
- A single `is_blank_row()` predicate (all three fields empty after normalization) cleanly covered both "blank line" and "row that's just commas" edge cases without duplicated logic.
- The plan-mode round of clarifying questions front-loaded the ambiguous design decisions (unknown-status labeling, count-all-rows vs. exclude-incomplete, case normalization) so the implementation phase had zero back-and-forth.

### Notable limitations or surprises

- See Tool & Workflow Note above (Python 3.11→3.14 constraint correction; no other surprises).

### Follow-up / next steps

- None outstanding — all planned steps (code, tests, docs, `.gitignore`) completed and verified. `commit`/`draft-pr` skills remain to be invoked, pending explicit approval, once this deliverable is reviewed.

---
