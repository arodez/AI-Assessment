# Verification Note

> 5–8 lines. Honesty is graded; "the AI made no mistakes" is almost never true and reads as a red flag.

**1. What the AI got wrong (or almost wrong):**
The original `solution.py` opened the CSV with plain `encoding="utf-8"`. When I stress-tested it against a synthetic CSV with a UTF-8 BOM (a very common artifact of Excel "Save As CSV" exports), the BOM attached itself to the first header name, turning `name` into `﻿name`. Every `row.get("name")` lookup then silently returned `None`, and every row — including perfectly valid ones with real emails and a `pending` status — was misclassified as `invalid` and dropped from both the counts and `pending.txt`. No crash, no error message — just silently wrong output, which is the worst kind of bug for this task.

**2. How I caught it:**
I didn't trust the two malformed rows already in the provided sample file as a full edge-case test, so I built a handful of synthetic CSVs (blank lines, missing name, missing email, whitespace/mixed-case status, extra trailing column, header-only file, nonexistent file, and finally a BOM-prefixed file) and ran `solution.py` against each one, inspecting stdout counts and `pending.txt` by hand.

**3. How I confirmed the final result is correct:**
Fixed by switching to `encoding="utf-8-sig"` (strips a BOM if present, no-op if absent), then re-ran the BOM test — the row was correctly counted under `pending` and its email appeared in `pending.txt`. I then re-ran against the real `data/engineers.csv` and manually tallied the file by eye: 3 `completed`, 3 `pending` (Luis, Diego, Jorge), 2 `in_progress`, and 2 rows with empty/missing `course_status` bucketed as `unknown` without crashing — this matched the script's printed output and the final `pending.txt` exactly.
