# Bugs found in `report_generator.py`

All four were reproduced by actually running the script (or isolated calls to its functions)
against `data/sample_input.csv`, not just asserted by the AI.

---

## Bug 1 — Mutable default argument corrupts state across runs

**Symptom:** if `load_engineers()` is called more than once in the same process (e.g. two test
cases, or the report generator invoked as a library rather than a fresh `python` process each
time), the second call returns *double* the correct number of engineers, all duplicated.

**Reproduction:**
```
$ python3 -c "
import report_generator as rg
e1 = rg.load_engineers('data/sample_input.csv')
print('First call count:', len(e1))
e2 = rg.load_engineers('data/sample_input.csv')
print('Second call count:', len(e2))
print('Same list object?', e1 is e2)
"
First call count: 8
Second call count: 16
Same list object? True
```

**Root cause:** `def append_row(row, rows=[])` (line 5) — the default list is created once,
at function-definition time, and shared by every call that doesn't pass `rows` explicitly.
`load_engineers` never passes `rows`, so every row from every call ever made in the process
lands in the same list.

**Fix:** never use a mutable default argument; build the list locally inside `load_engineers`
and return it, or default to `None` and create a fresh list when `rows is None`.

---

## Bug 2 — Skip counter never increments (dead code after `continue`)

**Symptom:** the report always prints `skipped rows: 0`, even when rows are actually dropped
(e.g. the truncated "Renata Vega" row in the sample, which has only 3 columns instead of 5).

**Reproduction:** ran the original script on the sample data —
```
$ python3 report_generator.py data/sample_input.csv /tmp/out.txt && cat /tmp/out.txt
...
skipped rows: 0
```
— despite the CSV containing one malformed row (`Renata Vega,renata.vega@example.com,Mobile`,
missing `status`/`deadline`) that raises `IndexError` and is caught by the `except`.

**Root cause:** in `load_engineers` (lines 23-25):
```python
except:
    continue
    SKIPPED += 1
```
`continue` immediately restarts the loop, so `SKIPPED += 1` is unreachable dead code — it
never runs, regardless of how many rows are skipped.

**Fix:** increment the counter *before* continuing, and (as part of the refactor requirement
to remove global mutable state) return the skip count from `load_engineers` instead of
mutating a module-level global.

---

## Bug 3 — Status counting is case/whitespace sensitive, silently drops rows

**Symptom:** engineers whose status is `Pending` (capitalized) or `in_progress ` (trailing
space) are not counted under any status at all — they vanish from the report instead of being
tallied correctly.

**Reproduction:** sample data has `Diego Fuentes` with status `Pending` (row 4) and
`Valeria Nunez` with status `in_progress ` (row 7, trailing space). Running the original
script gives:
```
completed: 3
pending: 2
in_progress: 1
```
but the correct tally (case/whitespace-insensitive) is `completed: 3, pending: 3,
in_progress: 2` — Diego and Valeria are missing from every bucket.

**Root cause:** `count_by_status` compares `s == 'completed'` / `'pending'` /
`'in_progress'` with exact string equality, so any casing or whitespace variation (which the
CSV demonstrably contains) falls through all three branches and is dropped.

**Fix:** normalize with `s.strip().lower()` before comparing/counting.

---

## Bug 4 — Overdue check compares dates as raw strings

**Symptom:** an engineer with a non-zero-padded deadline that is genuinely overdue is missing
from the `overdue engineers:` list.

**Reproduction:** sample data has `Jorge Salinas`, status `pending`, deadline `2026-5-30`
(month not zero-padded). "Today" defaults to `2026-07-14`, so May 30 2026 is clearly overdue.
Running the original script, the overdue list is:
```
overdue engineers:
  - luis.mendoza@example.com
  - diego.fuentes@example.com
  - valeria.nunez@example.com
```
— Jorge is absent even though he should be overdue.

**Root cause:** `overdue()` does `e['deadline'] < today` as a plain string comparison.
Lexicographically, `'2026-5-30' > '2026-07-14'` (because the character `'5'` sorts after
`'0'` at that position), so the non-zero-padded date is incorrectly treated as being in the
future.

**Fix:** parse both `deadline` and `today` into real `datetime.date` objects before comparing,
so comparison follows calendar order rather than string/lexicographic order.
