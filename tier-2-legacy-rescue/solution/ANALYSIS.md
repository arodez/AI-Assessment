# Analysis of `report_generator.py`

**Purpose:** generates a weekly plaintext training-compliance report from a CSV of engineer
training records.

**CLI:** `python report_generator.py <input.csv> <output.txt>` — no other args, no flags.

**Input (`argv[1]`):** CSV with header row and columns `name, email, team, status, deadline`
(the sample file's header spells the status column `course_status`, but the code reads it
positionally, so the header text itself is never checked). `deadline` is assumed to be an ISO
`YYYY-MM-DD` string; `status` is assumed to be exactly `completed`, `pending`, or `in_progress`.

**Output (`argv[2]`):** plaintext report with:
- a title line,
- one `status: count` line per status seen,
- a `skipped rows: N` line for malformed rows,
- an `overdue engineers:` section listing the email of every engineer whose status isn't
  `completed` and whose deadline is before "today" (hardcoded default `2026-07-14`).

**Structure:** four small functions plus `main`:
- `append_row(row, rows=[])` — accumulates parsed rows into a list.
- `load_engineers(path)` — reads the CSV, builds a dict per row, skips rows that error out.
- `count_by_status(engineers)` — tallies engineers per status.
- `overdue(engineers, today=...)` — returns emails of non-completed engineers past deadline.
- `main()` — wires the above together and writes the report.

**Data assumptions the code silently relies on** (and gets wrong on the sample data): status
values are exact-case, no surrounding whitespace; deadlines are always zero-padded
`YYYY-MM-DD`; every data row has exactly 5 columns.
