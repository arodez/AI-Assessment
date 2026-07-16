# Bug Reports for `report_generator.py`

Below are the 4 identified bugs in the legacy script, including their symptoms, root causes, and fixes.

---

### Bug 1 (B1): Mutable Default Argument in `append_row`

*   **Symptom:** When running multiple reports sequentially in the same Python process, or when running automated test suites, the status counts of subsequent runs inflate because data from previous runs is retained.
*   **Root Cause:** The function signature is defined as `def append_row(row, rows=[])`. In Python, default arguments are evaluated once when the function is defined, meaning all calls to `append_row` that omit the `rows` argument share the same list instance.
*   **Fix:** Change the signature to `def append_row(row, rows=None)`. If `rows` is `None`, initialize it to a new list `[]`. Additionally, update the call site in `load_engineers` to pass the accumulated list `engineers` so that the rows actually collect: `engineers = append_row(..., engineers)`.

---

### Bug 2 (B2): Case and Whitespace Sensitivity in `count_by_status`

*   **Symptom:** Valid records in the CSV containing statuses like `"Pending"` (capitalized) or `"in_progress "` (with trailing whitespace) are silently ignored and omitted from the report statistics.
*   **Root Cause:** The status checks are hardcoded to exact lowercase strings: `s == 'completed'`, `s == 'pending'`, and `s == 'in_progress'`. No string normalization (lowercasing or whitespace stripping) is applied.
*   **Fix:** Normalize the status string by calling `.strip().lower()` before performing the comparisons.

---

### Bug 3 (B3): Lexicographical String Comparison for Deadlines

*   **Symptom:** Overdue engineers with non-zero-padded dates (e.g., `'2026-5-30'`) are misclassified and do not appear in the overdue list relative to the cutoff date `'2026-07-14'`.
*   **Root Cause:** The condition `e['deadline'] < today` compares raw strings lexicographically instead of comparing dates chronologically. Since `'5'` (from `'2026-5-30'`) comes after `'0'` (from `'2026-07-14'`), the string comparison evaluates as false, even though May 30 is in the past.
*   **Fix:** Convert both dates to proper `datetime.date` objects using `datetime.datetime.strptime().date()` before comparing. Also, parse dates in multiple formats (e.g., zero-padded and non-zero-padded) to handle varying input data.

---

### Bug 4 (B4): Dead Skipped-Row Counter and Lack of Global Scope

*   **Symptom:** The final report always outputs `skipped rows: 0`, even when rows are malformed and raise exceptions during CSV parsing (e.g., `Renata Vega`).
*   **Root Cause:** 
    1. In the `except:` block of `load_engineers`, the statement `SKIPPED += 1` is placed after the `continue` statement, making it completely unreachable.
    2. Even if it were reached, `SKIPPED` is a global variable, and modifying it inside `load_engineers` without a `global SKIPPED` statement would raise an `UnboundLocalError`.
*   **Fix:** Declare `global SKIPPED` at the beginning of `load_engineers`, and place `SKIPPED += 1` before `continue` in the `except` block.

---

## False Positives Investigated and Rejected

During our analysis, the AI assistant flagged the following items as potential bugs. We investigated and rejected them:

1.  **AI Claim:** The line `return engineers or []` is redundant or buggy because `engineers` could be `None`.
    *   **Investigation:** In Python, `engineers or []` is standard, idiomatically safe syntax. If `engineers` is `None` or an empty list, it correctly evaluates to `[]`. This is not a bug.
2.  **AI Claim:** `csv.reader` requires `newline=''` when opening the file to avoid blank line issues on Windows.
    *   **Investigation:** While specifying `newline=''` in `open` is a recommended best practice for the CSV module, the legacy script is running under POSIX constraints where default newlines are handled correctly by Python's universal newlines, and it is not the cause of any crashes or incorrect statistics in the current scope.
