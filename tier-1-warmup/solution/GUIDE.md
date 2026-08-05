# GUIDE

## Overview

`solution.py` is a CLI that reads a CSV of engineers (`name`, `email`, `course_status`), prints a total count and a per-status breakdown, and writes the emails of engineers in `pending` status to a timestamped `pending-<timestamp>.txt` file. All three CSV columns are treated as optional, and malformed rows (missing columns, blank values, extra columns) are handled without crashing.

## Installation

Requires Python 3.14+ (this project was built and tested against 3.14.6 — the only interpreter available on the dev machine) and [Poetry](https://python-poetry.org/).

```bash
brew install poetry
# or, if you don't use Homebrew:
curl -sSL https://install.python-poetry.org | python3 -
```

From the `solution/` directory:

```bash
poetry install
```

This creates a virtualenv and installs `pytest` as a dev dependency. `solution.py` itself has no third-party dependencies — it only uses the Python standard library.

## Usage

```bash
poetry run python solution.py path/to/engineers.csv
```

Example, against this repo's sample data:

```bash
poetry run python solution.py ../data/engineers.csv
```

```
Processed total engineers: 10
3 engineers in completed status
2 engineers in in_progress status
3 engineers in pending status
2 engineers in unknown status
Pending results generated in pending-2026-08-04T16-46-24.txt
```

- The first line is the total number of non-blank rows processed.
- One line per distinct `course_status`, sorted alphabetically.
- The last line names the file just written, in the directory the command was run from.

`pending-<timestamp>.txt` (created in the current working directory, **not** next to the input CSV) contains one email per line for every row whose status is `pending`:

```
luis.mendoza@example.com
diego.fuentes@example.com
jorge.salinas@example.com
```

## Design decisions & edge-case handling

| Situation                                                     | Behavior                                                                                                                                                                                                        |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Entirely blank line, or a row that's just commas (`,,`)       | Excluded — doesn't count toward the total or any status.                                                                                                                                                        |
| Missing/blank `course_status`                                 | Counted, grouped under the label `unknown`.                                                                                                                                                                     |
| `course_status` case/whitespace (`" Pending "`, `"PENDING"`)  | Normalized (trimmed + lowercased) before matching/grouping — all variants of "pending" count as one group.                                                                                                      |
| Missing `name` and/or `email`, but at least one field present | Row still counts toward the total and its status group.                                                                                                                                                         |
| `pending` row with a blank `email`                            | Counted in the status tally, but has nothing to contribute to the pending emails file.                                                                                                                          |
| Duplicate rows                                                | Not de-duplicated — each occurrence is counted and, if pending, its email is written again.                                                                                                                     |
| Extra/unexpected columns                                      | Ignored.                                                                                                                                                                                                        |
| Non-UTF-8 file                                                | Re-read with replacement characters for undecodable bytes and a warning printed to stderr, rather than crashing.                                                                                                |
| Where `pending-<timestamp>.txt` is written                    | Current working directory of the invocation, not next to the input CSV — the input may live in a shared/reference `data/` folder that generated output shouldn't pollute, and no `--output` flag was requested. |
| Timestamp format                                              | ISO 8601 (`isoformat(timespec="seconds")`) with `:` replaced by `-`, since colons are awkward/invalid in filenames on some filesystems, e.g. `2026-08-04T16-46-24`.                                             |

## Contributing

### Gitflow

- Branch off `main` for any change (this solution was built on `JavierCA_Solution_WarmUp`).
- Use the repo's `commit` skill (`.claude/skills/commit/`) to draft Conventional Commits-formatted messages from the staged diff — don't hand-roll commit messages.
- Use the `draft-pr` skill (`.claude/skills/draft-pr/`) to open a **draft** PR via `gh pr create` once a branch is ready for review. Both skills ask for explicit approval before their side-effecting step (commit / PR creation).

### Development environment (Poetry)

```bash
cd solution

# Install/update dependencies (creates a virtualenv if needed)
poetry install

# Activate an interactive shell inside the virtualenv
poetry shell
# ... work interactively ...
exit                     # deactivate, back to your normal shell

# Or run one-off commands without activating a shell
poetry run python solution.py ../data/engineers.csv
poetry run pytest
```

### Running and adding tests

```bash
poetry run pytest -v
```

- Test fixtures (CSV files, each isolating one behavior) live in `tests/fixtures/`.
- Tests live in `tests/test_solution.py`, following a one-fixture-one-test pattern for parsing/counting behavior, plus unit tests for individual helper functions and end-to-end tests that invoke `solution.main()` directly.
- All tests that write a `pending-*.txt` file do so inside pytest's `tmp_path` fixture (via `monkeypatch.chdir(tmp_path)`), so running the suite never writes into `solution/` itself.
- To add a new edge case: drop a new CSV into `tests/fixtures/`, add a row to the fixture table in this file, and add a corresponding test function in `tests/test_solution.py`.

## Reporting an error

This is a private assessment repo with no issue tracker. If you (or an AI assistant) find a bug — including something the AI got wrong while building this — note it in [VERIFICATION_NOTE.md](VERIFICATION_NOTE.md) under "what the AI got wrong," or, for a design-level limitation rather than a one-off mistake, add a bullet to a "Known Issues" section at the bottom of this file.

### Known Issues

- None currently known.
