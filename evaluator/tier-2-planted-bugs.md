# Tier 2 — Planted bugs answer key

| # | Bug | Location | Symptom | Root cause |
|---|-----|----------|---------|-----------|
| B1 | Mutable default argument | `append_row(row, rows=[])` | Counts inflate if functions are called more than once in a process (e.g., from tests or reuse) | Default list is shared across calls |
| B2 | Case-sensitive, unstripped status matching | `count_by_status` | Rows like `Pending` or `in_progress ` (trailing space) silently vanish from counts | Exact `==` comparison, no `.strip().lower()` |
| B3 | String date comparison | `overdue()` | `2026-9-05` (non-zero-padded) compares lexicographically; engineers misclassified as overdue/not overdue | `e['deadline'] < today` compares strings, not dates |
| B4 | Dead skipped-row counter | `load_engineers` | Report always says `skipped rows: 0` even when rows are malformed; bare `except` also swallows unrelated errors | `SKIPPED += 1` sits after `continue` (unreachable); `SKIPPED` is also a global never declared with `global` (would raise UnboundLocalError if reached) |

**Note:** the provided `data/sample_input.csv` already triggers B2 (rows `Diego…,Pending` and `Valeria…,in_progress `), B3 (`2026-9-05`), and B4 (short row `Renata Vega`). Strong candidates will notice this; it's also acceptable if they build their own edge-case CSVs instead.

**Grading notes**
- "Found" = symptom + correct root cause + reproduction (failing test or demonstrated run).
- Common false positives to watch for (score against): claiming `engineers or []` is itself a bug, claiming `csv.DictReader` needs `newline=''` as a *defect*, style complaints framed as bugs.

## Expected output on `data/sample_input.csv` (today hardcoded as 2026-07-14)

**Buggy script produces:**
```
completed: 3
pending: 2          <- B2: "Pending" (Diego) dropped
in_progress: 1      <- B2: "in_progress " (Valeria, trailing space) dropped
skipped rows: 0     <- B4: Renata's short row silently swallowed
overdue: luis, diego, valeria   <- B3: Jorge (deadline 2026-5-30, truly overdue) missing due to string comparison
```

**Correct output should be:**
```
completed: 3, pending: 3, in_progress: 2, skipped rows: 1
overdue: luis, diego, jorge, valeria (4)
```
