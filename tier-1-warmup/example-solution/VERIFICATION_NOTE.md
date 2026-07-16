# Verification Note

> 5–8 lines. Honesty is graded; "the AI made no mistakes" is almost never true and reads as a red flag.

**1. What the AI got wrong (or almost wrong):**  
The AI initially used GNU awk's `asorti()` extension to sort status counts alphabetically. This is not POSIX-portable and broke immediately on macOS, which uses BSD awk by default.

**2. How I caught it:**  
I ran the generated `solution.sh` on my macOS workstation. It crashed with `awk: calling undefined function asorti`.

**3. How I confirmed the final result is correct:**  
I tested the updated script with:
1. `data/engineers.csv` (happy path + malformed rows): counts matched exactly (completed: 3, pending: 3, in_progress: 2, skipped: 2) and `pending.txt` contained only the 3 valid emails.
2. A missing file: it returned the correct error message and exit code 1.
3. An empty/header-only file: it handled it cleanly without syntax errors.
