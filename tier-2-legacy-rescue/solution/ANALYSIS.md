# Audit: `report_generator.py`

## Purpose

Generates a plain-text weekly training-compliance report from a CSV export of engineers. For each engineer it tracks a training `status` (`completed` / `pending` / `in_progress`) and a `deadline`; the report summarizes how many engineers fall into each status and lists who is overdue (not completed, past deadline).

## Expected input

A CSV file, path given as `argv[1]`, with a header row followed by data rows. Columns are read **positionally**, not by header name:

| index | field    | notes |
|-------|----------|-------|
| 0 | name | free text |
| 1 | email | used as the sole engineer identifier in the report |
| 2 | team | read but never used in output |
| 3 | status | expected to be exactly `completed`, `pending`, or `in_progress` |
| 4 | deadline | expected to be an ISO date string, `YYYY-MM-DD`, zero-padded |

Because parsing is positional, the header's actual text (e.g. `course_status` in `data/sample_input.csv`) is irrelevant to the code — only column order matters. Any row that's short a column, or otherwise raises during dict construction, is meant to be dropped silently.

## Expected output

A UTF-8 text file, path given as `argv[2]`:

```
WEEKLY TRAINING COMPLIANCE REPORT
completed: <n>
pending: <n>
in_progress: <n>
skipped rows: <n>
overdue engineers:
  - <email>
  - <email>
```

Only statuses actually present in the data get a line (there's no zero-fill for unseen statuses).

## Structure

Single file, four functions, no classes, one module-level global:

- `SKIPPED` (module global) — intended running count of unparseable rows.
- `append_row(row, rows=[])` — appends `row` to `rows` and returns it. Used as an accumulator inside `load_engineers`.
- `load_engineers(path)` — opens the CSV, skips the header, and builds one dict per row via `append_row`. Wraps each row in a bare `try/except` so malformed rows don't crash the run.
- `count_by_status(engineers)` — tallies engineers into a `{status: count}` dict via exact string equality against the three known statuses.
- `overdue(engineers, today='2026-07-14')` — returns the emails of engineers whose status isn't `'completed'` and whose `deadline` string is less than `today`, using plain string comparison (no date parsing).
- `main()` — CLI entry point: reads `argv[1]`/`argv[2]`, calls the three functions above in sequence, and writes the fixed-format report.

**Data flow:** CSV rows → list of engineer dicts (`load_engineers`) → `{status: count}` dict + list of overdue emails (`count_by_status`, `overdue`, both fed the same dict list) → flat text report (`main`).

## Strengths

- Small and linear — the whole pipeline is readable top to bottom in under 60 lines, with no hidden control flow.
- Row-level parsing failures are isolated with a `try/except` per row rather than letting one bad row abort the whole file.
- Functions are narrowly scoped (`load` / `count` / `filter` / `write`), which makes it straightforward to test each stage in isolation once the code is testable.

## Weaknesses

Observed by reading the code and, where noted, confirmed by running it against `data/sample_input.csv` (see commands below the table). These are candidates for the formal defect list in `BUGS.md`, not exhaustive on their own.

| Area | Issue | Evidence |
|---|---|---|
| Shared state | `append_row`'s default `rows=[]` is created once at function-definition time and reused across *every* call, in *every* run of the process — not a fresh list per call. | Calling `load_engineers()` twice in one process returns the same list object for both calls, with combined length (16 rows from two 8-row calls, `first is second == True`). |
| Accounting | The `except: continue` in `load_engineers` skips to the next row *before* `SKIPPED += 1` runs — that increment is unreachable dead code. Even if it were reached, `SKIPPED` is assigned without a `global` declaration, which would raise `UnboundLocalError` inside the function. | Sample input has one short row (`Renata Vega`, missing `status`/`deadline`) that is silently dropped; the generated report still prints `skipped rows: 0`. |
| Data normalization | Status matching in `count_by_status` is an exact, case-sensitive, unstripped string comparison against three literals. Any variance (capitalization, stray whitespace) fails all three branches and the row disappears from the counts with no signal. `overdue()` instead treats *anything not equal to `'completed'`* as active, so the two functions disagree on what counts as a valid/known status. | Sample input has `Pending` (capitalized) and `in_progress ` (trailing space) — both are excluded from `count_by_status`'s tallies, but the `Pending` row still appears in the overdue list, showing the inconsistency directly in one report run. |
| Date logic | `overdue()` compares `deadline` and `today` as plain strings. This only produces correct results if every date is zero-padded ISO-8601; a non-padded month/day (e.g. `2026-5-30`) sorts *after* `2026-07-14` lexicographically even though the actual date is earlier. | Sample input's `Jorge Salinas` has deadline `2026-5-30` and status `pending`; despite being months overdue, he's absent from the generated `overdue engineers` list. |
| Robustness | The bare `except:` in `load_engineers` catches everything, including programming errors unrelated to bad data, which makes future regressions in this function silent instead of loud. | — |
| Robustness | No validation of `sys.argv` length or file existence; missing arguments or a bad path surface as a raw, user-unfriendly traceback. | — |
| Testability | `SKIPPED` (global) and `append_row`'s default-list accumulator are both process-lifetime mutable state, so results depend on call history within a process — a script that should be a pure function of its input file isn't one. | Same evidence as the "Shared state" row above. |

Reproduction commands used above:
```bash
python3 report_generator.py data/sample_input.csv /tmp/report.txt   # inspect skipped-rows and overdue lines
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('rg', 'report_generator.py')
rg = importlib.util.module_from_spec(spec); spec.loader.exec_module(rg)
a = rg.load_engineers('data/sample_input.csv')
b = rg.load_engineers('data/sample_input.csv')
print(len(a), len(b), a is b)
"
```

## Suggested improvements

- Replace the mutable default argument with a fresh list built inside `load_engineers`; drop `append_row` entirely or make it a pure function that doesn't rely on a default-arg accumulator.
- Replace the module-level `SKIPPED` global with a return value (e.g. have `load_engineers` return `(engineers, skipped_count)`, or return a small result object) so the function is a pure mapping from path to data.
- Normalize `status` once at load time (`strip().lower()`), validate it against an explicit set of known values, and route unknown values into the skipped/warning count instead of silently dropping them from every downstream calculation.
- Parse `deadline` into a `datetime.date` at load time (`datetime.strptime(value, '%Y-%m-%d')`) and compare `date` objects instead of raw strings; treat unparsable dates the same way as other malformed rows.
- Replace the bare `except:` with a specific exception type (`(IndexError, KeyError)` for the current row-shape failures), and let genuinely unexpected exceptions propagate.
- Default `today` to `datetime.date.today()` rather than a fixed literal, while still allowing an explicit override for reproducible/testable runs.
- Validate `sys.argv` up front and fail with a clear usage message rather than an unguarded `IndexError`/`FileNotFoundError` traceback.
- Add type hints and docstrings to each function to make the input/output contract explicit without needing to read the implementation.

## Open questions / assumptions — resolved

- **`team` (parsed but unused):** Keep it. The input schema is not to be changed, so `team` stays part of the engineer record even though nothing currently reads it downstream.
- **Unknown/malformed `status` values:** Give them their own `unknown: n` bucket in the report, separate from `completed` / `pending` / `in_progress`. Reserve `skipped rows: n` strictly for rows that raised an error while being parsed (missing columns, etc.) — a *known but unrecognized* status value is not a parse error and must not be conflated with one.
- **`deadline` presence:** Treat it as optional. Self-paced or optional courses may legitimately have no deadline, so a missing/blank `deadline` must not cause the row to be dropped or counted as skipped; it should simply be excluded from the `overdue` check (no deadline ⇒ cannot be overdue) while the engineer still counts normally in `count_by_status`.

These decisions change the target behavior of the fixed implementation beyond a literal bug-for-bug fix — the report format gains an `unknown` line, and `overdue()` and `load_engineers()` need to treat a blank `deadline` as valid input rather than a parse failure. This will be reflected in `BUGS.md` and `report_generator_fixed.py`.
