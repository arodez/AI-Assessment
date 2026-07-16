# Tier 3 — 30-minute review protocol

1. **(5 min) Commit history first.** `git log --oneline` — expect ≥10 incremental commits, conventions file committed first. Then `git log -p | grep -iE "api[_-]?key|secret|token"` for leaked secrets. A leaked secret = automatic fail on the security criterion.
2. **(10 min) Run the app** from README instructions alone. If it doesn't start from the README, cap "Working software" at Below.
3. **(10 min) Upload `data/trap_sample.csv`** and check:
   - The 2 malformed rows (Diego Fuentes — missing deadline; Camila Ortiz — `not-a-date` as deadline) are **reported**, not silently dropped.
   - `Pending` (capital P, e.g., Luis Mendoza) is counted as pending.
   - The boundary row Sofia Reyes (deadline = review date / system date at runtime) is handled according to the overdue ruling: she is **not** overdue, and the app uses the live system date for comparison.
   - Overdue list matches a hand count (only Luis Mendoza and Jorge Salinas are overdue).
4. **(5 min) Read `AI_USAGE.md` and spot-check the prompt log** against the commit history — they should tell the same story.

**Red flags:** no rejected-row reporting; string date comparisons; single-dump commit; AI-usage report in generic marketing language; prompt log that doesn't match the code.
