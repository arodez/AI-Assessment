# Prompt Log

## Tool & Workflow Note

**Tool used:** Claude (Anthropic), chat interface with code execution
(bash/Python sandbox).
**Mode(s) used:** chat + agentic code execution (the assistant ran the
original script and my own draft fixes directly against
`sample_input.csv` rather than just reasoning about the code in text).
**Notable limitations or surprises:**
- The AI's first suggested date fix (`datetime.date.fromisoformat`)
  looked correct and idiomatic, but turned out to be **wrong** —
  `fromisoformat` rejects non-zero-padded dates like `2026-5-30` even in
  Python 3.12, which is exactly the malformed-but-real value in the
  planted bug. This was only caught by actually running the fixed test
  suite and seeing it fail, not by inspection. Had to switch to a manual
  `split("-")` + `date(int, int, int)` parse.
- The AI initially flagged the CSV header name mismatch
  (`course_status` in the sample data vs. `status` expected by the
  script) as a possible 5th bug. This was rejected after checking that
  the script parses columns **by index**, not by header name — the
  header row is only ever consumed with `next(reader)` and discarded.
  Documented in `BUGS.md` as an explicitly-ruled-out false positive.
- No internet access in the sandbox, so `pytest` could not be installed.
  Tests were still authored as standard pytest-style functions (as
  required), but were verified locally with a small stand-in runner that
  calls each `test_*` function directly with a `tempfile`-backed
  `tmp_path`, plus a stub `pytest` module just to satisfy the `import
  pytest` line. This is noted so the grader understands why verification
  output doesn't show literal `pytest` CLI output — see
  `VERIFICATION_NOTE.md`.

---

### Prompt 1
**Mode:** agentic (chat + code execution)
```
Run report_generator.py against sample_input.csv and show me the raw
output, then load_engineers() directly and print every parsed row so I
can compare row count against the actual CSV.
```
**Outcome:** accepted — this was the starting point for everything else.
Confirmed the original silently drops rows (8 loaded vs 9 data rows,
`SKIPPED` reported as 0) and gave me the first hard data point to build
bug hypotheses from, rather than guessing from reading the code alone.

### Prompt 2
**Mode:** agentic (chat + code execution)
```
The SKIPPED counter looks broken — the increment is after a `continue`.
Confirm that's genuinely dead code, and check whether moving it before
`continue` would even work given SKIPPED is a module-level global.
```
**Outcome:** accepted — ran a minimal repro showing that even if
reordered, the missing `global SKIPPED` declaration would raise
`UnboundLocalError`. This upgraded the bug from "looks suspicious" to
"confirmed with two independent reproduction paths," which is what went
into `BUGS.md`.

### Prompt 3
**Mode:** agentic (chat + code execution)
```
count_by_status only matches exact strings 'completed'/'pending'/
'in_progress'. The sample CSV has 'Pending' (capitalized) and
'in_progress ' (trailing space). Confirm whether these rows disappear
from the counts entirely, with numbers.
```
**Outcome:** accepted — ran `count_by_status` against the loaded
engineers and compared `sum(counts.values())` to `len(engineers)`: 6 vs
8, a 2-row gap matching exactly the two malformed-status rows. This
quantitative mismatch is what's cited in `BUGS.md` rather than just
"this looks like it could be a bug."

### Prompt 4
**Mode:** agentic (chat + code execution)
```
overdue() compares deadline strings directly with `<`. sample_input.csv
has '2026-5-30' (no zero-padding) for Jorge Salinas. Show me the actual
Python string comparison result vs. what a correct date comparison would
give, and confirm Jorge is missing from the original script's overdue
list.
```
**Outcome:** accepted — `'2026-5-30' < '2026-07-14'` evaluates to
`False` in a plain Python REPL check, while the zero-padded equivalent
evaluates to `True`. Cross-checked against the actual CLI output of the
original script, where Jorge is indeed absent from `overdue engineers`.

### Prompt 5
**Mode:** agentic (chat + code execution)
```
append_row uses `rows=[]` as a default argument. Show me concretely what
breaks if load_engineers() is called twice in the same process — don't
just explain the Python gotcha in the abstract, run it.
```
**Outcome:** accepted — ran `load_engineers` twice back to back in one
process; second call returned 16 rows instead of 8, and `first is
second` was `True`, proving the shared-list mutation directly rather
than citing "well-known Python footgun" without evidence.

### Prompt 6
**Mode:** agentic (chat + code execution)
```
Is the CSV header mismatch (course_status vs status) a real bug, or does
the script not care about header names at all?
```
**Outcome:** rejected as a bug — confirmed the script reads by column
index (`row[3]`), never by header name; the header row is discarded via
`next(reader)`. Recorded as a ruled-out false positive in `BUGS.md`
rather than silently dropped, per the assignment's instruction that
every reported bug must be reproduced and hallucinated bugs count
against the submission.

### Prompt 7
**Mode:** agentic (chat + code execution)
```
Draft report_generator_fixed.py: type hints, docstrings, no bare
excepts, no global mutable state, same CLI interface, fixes for all 4
confirmed bugs. Use date.fromisoformat for the deadline parsing.
```
**Outcome:** modified — the draft used `date.fromisoformat`, which
rejects `'2026-5-30'` (raises `ValueError` even though it's a valid,
just non-zero-padded, calendar date). This was caught in the next step
(test run), not by inspection, and fixed by replacing it with a manual
`split("-")` + `date(int, int, int)` parse that tolerates missing
zero-padding, which is what the real input data requires.

### Prompt 8
**Mode:** agentic (chat + code execution)
```
Write test_report_generator.py against report_generator_fixed.py: one
test per confirmed bug plus a few edge cases, minimum 5 tests. Then
actually run them (pytest isn't installed, so wire up a manual runner)
and show me pass/fail per test — don't just assert they'd pass.
```
**Outcome:** modified — first run surfaced 2 real failures: (1) the
`fromisoformat` bug from Prompt 7, and (2) an arithmetic mistake I made
in my own expected test value (`pending: 2` should have been `pending:
3`, since Jorge Salinas is also `pending` and I'd miscounted by hand).
Both were fixed and the suite re-run to confirm all 8 unit tests pass
against the fixed implementation.

### Prompt 9
**Mode:** agentic (chat + code execution)
```
The assignment says tests must fail against the original
report_generator.py when imports are swapped. The unit tests import
Engineer/LoadResult, which don't exist in the original, so they'll just
ImportError instead of demonstrating the actual bug. Add a black-box
CLI/subprocess test layer that runs either script as a subprocess and
checks the report text, so swapping SCRIPT_PATH to the original actually
demonstrates the bugs behaviorally, not just as a naming mismatch. Then
run those specifically against the original and show me the result.
```
**Outcome:** accepted — added `test_cli_*` functions using
`subprocess.run` against a `SCRIPT_PATH` constant. Ran them with
`SCRIPT_PATH` pointed at the original `report_generator.py`: 3 of 4
failed (skipped-row count, dropped status counts, missed overdue date),
confirming bugs 1–3 behaviorally. Documented in the test file that bug 4
(mutable default) does not reproduce at the CLI layer because each CLI
invocation is a fresh process — it's caught instead by the in-process
unit test `test_load_engineers_does_not_leak_state_between_calls`.
