# Developer Guide: report_generator_fixed

Practical guide for running the weekly training-compliance report generator
and for contributing to it. For *what* was fixed and *why*, see
[`ANALYSIS.md`](ANALYSIS.md) and [`BUGS.md`](BUGS.md); this document is
about *how to work with the code day to day*.

## How to use the tool

The CLI takes exactly two positional arguments and doesn't change based on
who's running it or when:

```bash
python report_generator_fixed.py <input.csv> <output.txt>
```

Example, using the sample data shipped with this repo:

```bash
poetry run python report_generator_fixed.py ../data/sample_input.csv report.txt
cat report.txt
```

Input is a CSV with a header row and, per engineer, `name`, `email`,
`team`, a course/training `status` (`completed`, `pending`, or
`in_progress` — anything else is still reported, under an `unknown`
bucket), and an optional `deadline` (`YYYY-MM-DD`, zero-padding not
required). Columns are matched by header name, so their order in the file
doesn't matter.

Output is a plain-text report:

```
WEEKLY TRAINING COMPLIANCE REPORT
completed: 3
pending: 3
in_progress: 2
skipped rows: 1
overdue engineers:
  - jorge.salinas@example.com
```

Status lines only appear when their count is greater than zero, and only
for the four recognized buckets (`completed`, `pending`, `in_progress`,
`unknown`), always in that order regardless of the order rows appeared in
the source CSV. `overdue engineers` lists anyone whose deadline has passed
and whose status isn't `completed` — see `overdue()`'s docstring in
[`report_generator_fixed.py`](report_generator_fixed.py) for the exact
rule, including the one inconsistency that was deliberately preserved
rather than fixed (documented in `ANALYSIS.md`).

**Exit codes:** `0` on success, `2` if the arguments are wrong (usage
message on stderr), `1` if the input file doesn't exist (named in the
stderr message). A row that fails to parse is dropped and counted under
`skipped rows` rather than crashing the run.

## How to contribute

### Gitflow guidelines

This repo's branches follow a `<name>_Solution[_<task>]` pattern off
`main`, e.g. `JavierCA_Solution_LegacyRescue`. When working on this
solution:

1. **Branch from your working branch, not `main` directly.** `main` (and,
   in a Claude Code session, the base `_Solution` branch) is guarded
   against direct pushes by [`.claude/hooks/protect-branches.sh`](../.claude/hooks/protect-branches.sh)
   — note that hook only governs Claude Code sessions that load it, not a
   plain terminal `git push`, so treat "don't push straight to `main`" as
   the actual rule and the hook as a backstop, not the enforcement
   mechanism itself.
2. **Commit with [Conventional Commits](https://www.conventionalcommits.org/)** —
   `<type>(<scope>): <description>`, imperative mood, no trailing period:

   | Type | Use for |
   |---|---|
   | `feat` | A new capability |
   | `fix` | A bug fix |
   | `docs` | Documentation only |
   | `refactor` | Restructuring without changing behavior |
   | `test` | Adding or correcting tests |
   | `chore` | Routine maintenance (deps, tooling config) |

   Example: `fix(overdue): compare parsed dates instead of raw strings`.
   The `commit` skill (`../.claude/skills/commit/`) drafts messages in this
   format from a staged diff if you're working with Claude Code.
3. **Keep commits reviewable.** One coherent change per commit — a bug fix
   and an unrelated formatting pass are two commits, not one.
4. **Open a PR before merging**, even for solo work — it's the natural
   place for the pre-commit checks (below) and CI, if configured, to run
   against the full diff. The `draft-pr` skill (`../.claude/skills/draft-pr/`)
   opens one via `gh pr create` from the current branch's commits.

### Python environment: install, activate, deactivate

Dependencies are managed with [Poetry](https://python-poetry.org/) from
inside this `solution/` directory (`pyproject.toml` lives here, not at the
repo root).

```bash
cd solution

# Install project + dev dependencies (pytest, mypy, ruff, pre-commit) into
# a dedicated virtualenv. Run this once, and again whenever pyproject.toml
# or poetry.lock changes.
poetry install
```

Day to day, prefer running commands through Poetry without activating
anything — it's one word longer but never leaves you wondering which
Python a bare `pytest` in your shell resolves to:

```bash
poetry run pytest
poetry run ruff check .
```

If you'd rather activate the environment directly in your shell (Poetry
≥2.0 doesn't ship `poetry shell` by default anymore):

```bash
# Activate: prints the activation command; eval it to run it in your
# current shell rather than a subshell.
eval "$(poetry env activate)"

# ...now `python`, `pytest`, `ruff`, `mypy` all resolve inside the venv...

# Deactivate: the standard venv deactivate function, left in your shell
# by activation.
deactivate
```

### How to execute the script, unit tests, and Ruff

```bash
# Run the script
poetry run python report_generator_fixed.py <input.csv> <output.txt>

# Run the full test suite (pytest.ini_options in pyproject.toml already
# wires in coverage — see "How to see the coverage" below)
poetry run pytest

# Run one file, one test, or a keyword match
poetry run pytest tests/unit/test_overdue.py
poetry run pytest tests/unit/test_overdue.py::test_deadline_equal_to_today_is_not_yet_overdue
poetry run pytest -k "overdue"

# Lint, and apply the auto-fixable subset
poetry run ruff check .
poetry run ruff check . --fix

# Check formatting, and apply it
poetry run ruff format --check .
poetry run ruff format .

# Static type checking (strict mode, whole solution/)
poetry run mypy .
```

### How to see the coverage

`pytest` is configured (in `[tool.pytest.ini_options]`, `pyproject.toml`)
to always measure coverage of `report_generator_fixed.py` and fail the
run if it drops below 100% — so a plain `poetry run pytest` already shows
you a per-file summary with any missing lines:

```
Name                        Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------
report_generator_fixed.py      94      0     18      0   100%
```

For a line-by-line, browsable view (which branch of an `if` was missed,
not just which line), open the generated HTML report:

```bash
poetry run pytest   # regenerates htmlcov/ as a side effect
open htmlcov/index.html
```

### How to add unit tests

- **Where:** `tests/unit/` for a single function in isolation, matching
  the module under test (`test_overdue.py` tests `overdue()`, etc.);
  `tests/integration/` for anything that goes through `main()` or shells
  out to the CLI. Add a new `test_*.py` file per function/concern rather
  than growing an existing one indefinitely.
- **Fixtures:** reuse what's in [`tests/conftest.py`](tests/conftest.py)
  before writing your own — `write_csv` (factory: writes rows + header to
  a temp CSV, returns its `Path`), `make_engineer` (factory: builds an
  `Engineer` with overridable defaults), `reference_today` (the fixed
  date `2026-07-14` used across the original bug scenarios, for
  deterministic `overdue`/`build_report` assertions), and
  `sample_csv_path` (path to the real `data/sample_input.csv`).
- **Style:** one behavior per test, name it after that behavior
  (`test_deadline_equal_to_today_is_not_yet_overdue`, not `test_overdue_2`).
  `pytest.mark.parametrize` for the same assertion over several inputs.
  Test functions don't need their own docstring (enforced by a
  `per-file-ignore` in `pyproject.toml`); modules and non-obvious design
  choices do — see the module docstrings in `tests/unit/test_overdue.py`
  or `tests/unit/test_load_engineers.py` for the level of detail expected
  when a test is pinning down a specific bug fix or a judgment call, not
  just a happy path.
- **Before you're done:** `poetry run pytest` must stay green at 100%
  coverage, and `poetry run ruff check tests`, `ruff format --check tests`,
  and `mypy tests` must all stay clean — the pre-commit hook (below)
  checks exactly this on every commit, so it's faster to check locally
  first.
- **If a test targets a specific defect**, reference it by number
  (`BUGS.md #6`) in a comment or docstring, the way the existing tests do
  — it saves the next person from having to reverse-engineer *why* a test
  asserts what it does.

### Pre-commit hooks

Installed once via (from `solution/`, after `poetry install`):

```bash
poetry run pre-commit install
```

This wires `../../.pre-commit-config.yaml` (repo root — see that file's
header comment for why) into a git hook that runs `ruff check`,
`ruff format --check`, `mypy`, and the full `pytest` + 100%-coverage gate
on every commit that touches this `solution/` directory. To run them
on demand without committing:

```bash
poetry run pre-commit run --all-files
```

To bypass on a deliberate work-in-progress commit (e.g. mid-refactor,
before coverage is back to 100%): `git commit --no-verify`. Don't make a
habit of it — it's an escape hatch, not a workflow.

### Project structure

```
solution/
├── ANALYSIS.md               # audit of the original script
├── BUGS.md                   # prioritized defect/gap backlog
├── GUIDE.md                  # this file
├── pyproject.toml            # Poetry project + pytest/coverage/mypy/ruff config
├── poetry.lock
├── report_generator_fixed.py # the implementation
└── tests/
    ├── conftest.py           # shared fixtures
    ├── unit/                 # one function/concern per test file
    └── integration/          # main()/CLI, including a black-box check
                               # that the *original* script still exhibits
                               # the documented bugs
```

## How to report an error

1. **Reproduce it first.** Run the script (or the specific function, in a
   `python -c` one-liner or a scratch test) against the smallest input
   that triggers the problem. A report without a reproduction is much
   slower for anyone to act on.
2. **Check it's not already tracked** in [`BUGS.md`](BUGS.md) or as an
   open issue.
3. **File it** — if this repo has GitHub issues enabled, use the `gh` CLI:

   ```bash
   gh issue create \
     --title "Short, specific summary of the wrong behavior" \
     --body "Scenario / Input / Output / Expected output — see below"
   ```

   Structure the body the same way `BUGS.md` documents each defect, since
   that format has already proven useful in this repo:

   | Field | What to include |
   |---|---|
   | **Scenario** | What you were doing and what code path is involved |
   | **Input** | The exact CSV row(s) or CLI invocation that triggers it |
   | **Output (current)** | What actually happens — paste the real output/traceback |
   | **Expected output** | What should happen instead |
   | **Severity** | Critical / High / Medium / Low — impact if it reaches a real report |
   | **Environment** | `poetry run python --version`, OS, and `git rev-parse HEAD` |

4. **If you can, add a failing test alongside the report** (or in the same
   PR that fixes it) — a test that fails on the current code and passes
   once fixed is the fastest way to get a bug both understood and closed
   for good, and is exactly the pattern this test suite already follows
   for every defect in `BUGS.md`.
