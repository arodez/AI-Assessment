# Verification Note

**1. What the AI got wrong (or almost wrong):**
Two real mistakes made it into a draft before being caught. First, the
initial fixed date-parsing used `date.fromisoformat`, which looked like
the "correct, idiomatic" fix but actually rejects the exact malformed
input the bug is about (`'2026-5-30'`, no zero-padding on the month) —
it would have silently turned a real bug into a different failure mode
(row gets discarded as unparseable instead of being correctly flagged
overdue). Second, the AI also initially proposed the CSV's
`course_status` vs. `status` header-name mismatch as a possible 5th bug,
which is a false positive: the script reads columns by index, not by
header name.

**2. How I caught it:**
Not by re-reading the code — by actually running things. The date bug
was caught because I insisted on running the test suite against the
fixed script rather than trusting that the tests "should" pass, and the
`test_overdue_detects_non_zero_padded_dates` test failed with a
`ValueError` at the load step. The header-name false positive was caught
by explicitly checking whether the script ever references header names
(it doesn't — `next(reader)` just discards the header row and everything
downstream uses `row[0]`..`row[4]` by position).

**3. How I confirmed the final result is correct** (tests run, manual checks, sample data used):
- Ran `report_generator.py` (original) against `sample_input.csv` and
  captured its literal output before changing anything, so every later
  claim could be diffed against real behavior instead of assumed.
- Reproduced each of the 4 bugs with a standalone script/REPL check
  before writing it into `BUGS.md` (row-count mismatch for bug 1,
  `sum(counts) != len(engineers)` for bug 2, direct string-vs-real-date
  comparison for bug 3, `first is second` identity check for bug 4).
- Ran the full `test_report_generator.py` suite (8 unit tests + 4 CLI
  black-box tests, 12 total) against `report_generator_fixed.py`: all
  pass.
- Re-ran just the 4 CLI black-box tests with `SCRIPT_PATH` swapped to
  point at the original `report_generator.py`: 4 of 4 fail
  (`test_cli_skipped_rows_are_counted`,
  `test_cli_status_counts_are_not_silently_dropped`,
  `test_cli_overdue_detects_non_zero_padded_dates`,
  `test_cli_runs_twice_without_accumulating_state`), which is the
  concrete evidence that bugs 1–4 are real and fixed. The AI mentions it
  just failed 3 of the 4th test, but running them manually actually shows
  the `test_cli_runs_twice_without_accumulating_state` as failed.
- Diffed the final report text for `sample_input.csv` between original
  and fixed side by side: `pending` 2→3, `in_progress` 1→2, `skipped
  rows` 0→1, and `jorge.salinas@example.com` newly appears in the
  overdue list — exactly the 4 rows affected by the 4 documented bugs,
  nothing else changed.

Note: `pytest` could not be installed in this sandbox (no network
access). Tests are written as standard pytest-compatible functions as
required, and were executed locally via a minimal stand-in runner that
imports the test module and calls each `test_*` function with a
`tempfile`-backed path in place of pytest's `tmp_path` fixture. This
should behave identically under a real `pytest` invocation
(`pytest test_report_generator.py -v`), since no pytest-specific
features beyond the `tmp_path` fixture signature are used.
