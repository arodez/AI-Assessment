# Plan: Engineer CSV Status CLI (`tier-1-warmup/solution/`)

## Context

The tier-1-warmup assessment (see [README.md](./README.md)) asks for a CLI that reads `data/engineers.csv` and reports counts per `course_status` plus a `pending` emails file, handling malformed rows gracefully. The user is upgrading the original bare-minimum spec into a fuller deliverable: proper CLI output formatting, a `/tests` folder with fixture-driven pytest coverage (happy path + edge cases), Poetry-based packaging/dependency management, and a `GUIDE.md` covering usage, contribution workflow, and environment setup. None of this exists yet — `solution/` is currently empty/nonexistent, and Poetry is not installed on this machine (only Python 3.14.6 is present).

Ambiguities were resolved with the user directly:
- **All non-blank rows count** toward "Total number of engineers," even with missing name/email.
- **Missing/blank `course_status` groups under the label `unknown`.**
- **Status matching is normalized**: trimmed + lowercased, so `" Pending "`, `"PENDING"`, `"pending"` are one group.
- **Poetry will be installed now** (via Homebrew) so `poetry install` / `poetry run pytest` can be verified end-to-end in this session.

Known-good expected numbers from the real sample data (`tier-1-warmup/data/engineers.csv`, 10 data rows): **10 total**, **3 pending** (Luis Mendoza, Diego Fuentes, Jorge Salinas), **3 completed**, **2 in_progress**, **2 unknown** (Marco Rivera — blank status; Isabel Vargas — missing column). This is the regression check used later.

`tier-2-legacy-rescue/report_generator.py` is a deliberately bad sibling example (bare `except`, mutable default arg, no `argparse`) — explicitly **not** a style precedent.

## Directory structure

```
tier-1-warmup/solution/
├── solution.py
├── pyproject.toml
├── poetry.lock                  # committed
├── GUIDE.md
├── PROMPT_LOG.md                # copied from ../PROMPT_LOG.md, filled in
├── VERIFICATION_NOTE.md         # copied from ../VERIFICATION_NOTE.md, filled in
└── tests/
    ├── test_solution.py
    └── fixtures/
        ├── happy_path.csv
        ├── header_only.csv
        ├── blank_lines.csv
        ├── missing_course_status_column.csv
        ├── blank_course_status.csv
        ├── missing_name.csv
        ├── missing_email.csv
        ├── mixed_case_whitespace_status.csv
        ├── duplicate_rows.csv
        ├── extra_columns.csv
        └── comma_only_row.csv
```

## `solution.py` design

Single stdlib-only module (`csv`, `argparse`, `datetime`, `pathlib`, `collections.Counter`, `sys`) so `tests/test_solution.py` can `import solution` directly. Functions:

- `read_raw_rows(csv_path)` — `csv.DictReader` over the file (`encoding="utf-8"`); a `UnicodeDecodeError` is caught, retried with `errors="replace"`, and a warning is printed to stderr instead of crashing. `DictReader`'s built-in behavior already handles the two known malformed-row shapes for free: short rows (e.g. `Isabel Vargas,isabel.vargas@example.com`) get `course_status=None` via `restval`; truly blank physical lines are skipped by `DictReader` itself; extra columns land under the ignored `restkey`.
- `normalize_row(raw)` → `{"name","email","course_status"}` with `None`→`""` and `.strip()` applied.
- `is_blank_row(row)` — `True` iff all three normalized fields are `""` (covers both blank lines and comma-only rows `,,` in one rule).
- `normalize_status(status)` — `status.strip().lower()`, or `"unknown"` if that's empty.
- `is_pending(status)` — `normalize_status(status) == "pending"`.
- `process_rows(raw_rows)` — normalize → drop blank rows → total count → `Counter` over `normalize_status(...)` → pending emails list (only rows where `is_pending()` **and** email is non-blank; a pending row with no email is counted in the tally but has nothing to write). No de-duplication anywhere — duplicates count and appear as written.
- `format_status_lines(counts)` — `f"{n} engineers in {status} status"`, **sorted alphabetically by status** for deterministic output/tests.
- `generate_timestamp(now=None)` — `(now or datetime.now()).isoformat(timespec="seconds").replace(":", "-")` (colons aren't filesystem-safe); `now` is injectable for deterministic tests.
- `pending_filename(timestamp)` → `f"pending-{timestamp}.txt"`.
- `write_pending_file(path, emails)` — one email per line, trailing newline.
- `main(argv=None)` — `argparse` with one required positional `csv_path`; validates the path exists (clean stderr message + exit 1 instead of a traceback if not); prints the three required output lines in order (`Processed total engineers: N`, sorted status lines, `Pending results generated in <filename>`); writes the pending file.

**Output location:** `pending-<timestamp>.txt` is written to the **current working directory the script is invoked from** (a bare relative filename — no path manipulation), not next to the input CSV, since the CSV may live in a shared/reference `data/` folder that shouldn't be polluted, and no `--output` flag was requested. Documented explicitly in GUIDE.md.

## `pyproject.toml`

```toml
[tool.poetry]
name = "engineer-status-cli"
version = "0.1.0"
description = "CLI that summarizes engineer course_status from a CSV and writes a pending-emails report."
authors = ["Javier Cervantes"]
package-mode = false

[tool.poetry.dependencies]
python = "^3.14"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"

[build-system]
requires = ["poetry-core>=1.8.0"]
build-backend = "poetry_core.masonry.api"
```

Only `pytest` is needed as a dev dependency (solution.py is stdlib-only). `python = "^3.14"` pins to the major line currently installed (3.14.6) — this is the only interpreter present on this machine, so the constraint reflects what's actually being tested rather than claiming broader compatibility that hasn't been verified. If `poetry install` still can't resolve a working env under 3.14 (unlikely, pytest ships universal wheels), fall back to `brew install python@3.12` + `poetry env use $(brew --prefix python@3.12)/bin/python3.12` and relax the constraint accordingly, noting it in VERIFICATION_NOTE.md if needed.

## Tests (`solution/tests/`)

One fixture CSV per edge case (table below), each loaded via `read_raw_rows`/`process_rows` in a dedicated test asserting exact total count, exact per-status `Counter`, and exact pending-email list:

| Fixture                            | Covers                                                                        |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| `happy_path.csv`                   | Well-formed rows across all statuses                                          |
| `header_only.csv`                  | Zero data rows → total 0, no status lines                                     |
| `blank_lines.csv`                  | Interspersed blank lines excluded from total                                  |
| `missing_course_status_column.csv` | 2-field rows (mirrors Isabel Vargas) → `unknown`, no crash                    |
| `blank_course_status.csv`          | Trailing empty 3rd field (mirrors Marco Rivera) → `unknown`                   |
| `missing_name.csv`                 | Blank name, valid email/status → still counted                                |
| `missing_email.csv`                | Blank email on a `pending` row → counted in tally, excluded from pending file |
| `mixed_case_whitespace_status.csv` | `"  Pending "`, `"PENDING"`, `"pending"` → one normalized group               |
| `duplicate_rows.csv`               | Exact duplicates → each counted, no de-dup                                    |
| `extra_columns.csv`                | 4th unexpected column → ignored, no crash                                     |
| `comma_only_row.csv`               | `,,` row mixed with valid rows → excluded (all fields blank)                  |

Plus in `test_solution.py`:
- Unit tests on pure helpers (`normalize_status`, `is_blank_row`, `is_pending`, `generate_timestamp` format, `pending_filename`).
- `write_pending_file` test writing into `tmp_path`.
- End-to-end test: `monkeypatch.chdir(tmp_path)`, call `solution.main([str(fixture)])`, assert stdout via `capsys`, glob `pending-*.txt` in `tmp_path` for contents (glob, not exact name, since timestamp is real-clock).
- **Regression test against the real sample data** (`tier-1-warmup/data/engineers.csv`, resolved via `Path(__file__).resolve()`, run with `monkeypatch.chdir(tmp_path)`): assert total=10, pending=3, completed=3, in_progress=2, unknown=2.
- All file-writing tests use `monkeypatch.chdir(tmp_path)` so nothing ever writes into `solution/` itself during the suite.

## `GUIDE.md` sections

1. Overview — what the tool does.
2. Installation — Python 3.14+ (3.14 confirmed working), install Poetry (`brew install poetry`, or the official installer as fallback), `cd solution && poetry install`.
3. Usage — `poetry run python solution.py ../data/engineers.csv`, annotated sample output, note on where `pending-*.txt` lands.
4. Design decisions & edge-case handling — table restating: blank/comma-only rows excluded; missing/blank status → `unknown`; case/whitespace-insensitive status matching; no de-dup; pending-without-email excluded from file but counted; output written to cwd; timestamp format.
5. Contributing / Gitflow — branch off `main` (this work is on `JavierCA_Solution_WarmUp`), use the repo's `commit` skill for Conventional Commits, use `draft-pr` skill for draft PRs.
6. Development environment — `poetry install`, `poetry shell` / `poetry run`, `exit` to deactivate.
7. Running/adding tests — `poetry run pytest -v`; where new fixtures/tests go.
8. Reporting an error — private assessment repo, no issue tracker: note it in `VERIFICATION_NOTE.md`'s "what the AI got wrong" section, or a "Known Issues" list in GUIDE.md for design-level limitations.

## Execution order

1. Create `solution/`, `solution/tests/`, `solution/tests/fixtures/`.
2. `brew install poetry`; verify `poetry --version`.
3. Write `pyproject.toml`.
4. Write `solution.py`.
5. `poetry lock && poetry install` from `solution/` — first checkpoint for the Python 3.14 resolution risk.
6. Write the 11 fixture CSVs.
7. Write `tests/test_solution.py`.
8. `poetry run pytest -v`; iterate until green.
9. Manually run the CLI against real sample data; confirm stdout and `pending-*.txt` match the expected numbers (10/3/3/2/2).
10. Write `GUIDE.md`.
11. Copy and fill in `PROMPT_LOG.md` and `VERIFICATION_NOTE.md` from `tier-1-warmup/` (the existing root-level blank copies) into `solution/`.
12. Add to `tier-1-warmup/.gitignore`: `__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `*.egg-info/`, `.pytest_cache/`, `solution/pending-*.txt` — do **not** ignore `poetry.lock`.
13. Remove any stray `pending-*.txt` from manual verification before committing.
14. Use the `commit` skill, then the `draft-pr` skill (both already require explicit approval before their side-effecting step — unaffected by this plan).

## Verification

```bash
cd tier-1-warmup/solution
brew install poetry && poetry --version
poetry install
poetry run pytest -v                              # expect all tests green, incl. regression test
poetry run python solution.py ../data/engineers.csv
# expect:
#   Processed total engineers: 10
#   3 engineers in completed status
#   2 engineers in in_progress status
#   3 engineers in pending status
#   2 engineers in unknown status
#   Pending results generated in pending-<timestamp>.txt
ls pending-*.txt && cat pending-*.txt              # expect exactly 3 lines (Luis/Diego/Jorge's emails)
rm pending-*.txt                                    # clean up before committing (also gitignored)
```

### Critical files
- `tier-1-warmup/solution/solution.py`
- `tier-1-warmup/solution/pyproject.toml`
- `tier-1-warmup/solution/tests/test_solution.py`
- `tier-1-warmup/data/engineers.csv` (reference input, unmodified)
- `tier-1-warmup/.gitignore` (add Python/Poetry entries)
