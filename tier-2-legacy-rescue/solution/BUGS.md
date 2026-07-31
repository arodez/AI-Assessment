# Identified Bugs in report_generator.py

The following critical defects have been identified in the codebase:

---

### 1. Mutable Default Argument & Mismatched Call Site
* **Location:** `append_row` (lines 5-7) and `load_engineers` (lines 16-22)
* **Root Cause:** `append_row` defines a mutable default argument `rows=[]`. In Python, default arguments are evaluated once at definition time, sharing the same list across all calls. Furthermore, `load_engineers` calls `append_row` without passing the accumulator list `engineers` as the second argument, relying entirely on this shared mutable list side-effect.
* **Impact:** 
  - Calling `load_engineers` multiple times accumulates and mixes data from previous invocations.
  - Correcting the mutable default argument alone without updating the caller breaks the program.
* **Fix:** Use `rows=None` in `append_row` and pass `engineers` explicitly:
  ```python
  def append_row(row, rows=None):
      if rows is None:
          rows = []
      rows.append(row)
      return rows
  
  # In load_engineers:
  engineers = append_row({ ... }, engineers)
  ```

---

### 2. Unreachable Skip Counter and Missing `global` Declaration
* **Location:** `load_engineers` (lines 3 & 23-25)
* **Root Cause:** In the `except` block, `SKIPPED += 1` is placed after the `continue` statement, making it unreachable. Additionally, `SKIPPED` is a global variable, but there is no `global SKIPPED` declaration inside the function scope to authorize modification.
* **Impact:** The skipped rows count is always reported as `0`. If the unreachable code were reached, it would raise an `UnboundLocalError`.
* **Fix:** Add `global SKIPPED` at the beginning of `load_engineers` and place the increment before `continue`:
  ```python
  except:
      global SKIPPED
      SKIPPED += 1
      continue
  ```

---

### 3. Unhandled `StopIteration` on Empty Files
* **Location:** `load_engineers` (line 13)
* **Root Cause:** `next(reader)` is called directly to skip the header row without checking if the file contains any content.
* **Impact:** If the CSV file is completely empty (0 bytes), the script crashes immediately with a `StopIteration` exception.
* **Fix:** Wrap the header read in a try-except block:
  ```python
  try:
      next(reader)
  except StopIteration:
      return []
  ```

---

### 4. Lexicographical Comparison of Malformed/Unpadded Dates
* **Location:** `overdue` (lines 40-45)
* **Root Cause:** The date comparison `e['deadline'] < today` performs string comparison. If dates in the input CSV are not zero-padded (e.g. `'2026-7-14'` instead of `'2026-07-14'`), lexicographical comparison fails because the character `'7'` is greater than `'0'`.
* **Impact:** Under-reporting or over-reporting of overdue status depending on the format of the date strings in the input data.
* **Fix:** Parse strings into `datetime.date` objects using `datetime.strptime` before comparing.

---

### 5. Case Sensitivity and Whitespace in Status Checking
* **Location:** `count_by_status` (lines 28-38)
* **Root Cause:** The status matching logic performs exact string checks (e.g., `s == 'completed'`). It does not normalize case or strip whitespace.
* **Impact:** Any record with status strings containing leading/trailing whitespace or uppercase characters (e.g., `'completed '` or `'Completed'`) will be silently ignored.
* **Fix:** Normalize the string using `.strip().lower()` before comparing.
