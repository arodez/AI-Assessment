# Prompt Log

> Record **every** prompt sent to the AI, in order, unedited. Add a one-line note on what you did with the response (accepted / modified / rejected). Exported chat links or screenshots may be attached instead, but the accept/modify/reject notes are still required.

## Tool & Workflow Note

**Tool used:** Antigravity (Gemini 3.5 Flash)  
**Mode(s) used:** chat & agent  
**Notable limitations or surprises:** The tool generated an elegant `awk` solution, but it initially used `asorti()`, which is a GNU awk extension. When run on macOS (which uses BSD awk by default), the script failed with `awk: calling undefined function asorti`. Had to iterate to make it POSIX-portable by sorting using an external `sort` pipeline instead.

---

### Prompt 1

**Mode:** chat
```
I need to write a shell script (solution.sh) that reads a CSV file at data/engineers.csv.
The file has columns: name, email, course_status.
The script should:
1. Print a count of how many engineers have each status
2. Write the email addresses of engineers with status "pending" to a file called pending.txt
3. Do NOT use Python, Perl, Ruby, or compiler languages. It must run as a standard portable shell script (sh/bash) using common tools like awk.
4. Handle edge cases: missing file, empty files, and malformed rows (e.g. missing columns, empty status values) gracefully without crashing.
```
**Outcome:** modified — the AI generated a `solution.sh` that used the GNU awk `asorti()` extension to print sorted status counts. Since I am running this on macOS, the script failed immediately because macOS's default awk is BSD-based and doesn't support `asorti`.

---

### Prompt 2

**Mode:** chat
```
The script failed on macOS with:
awk: calling undefined function asorti
Line number 43

Can you rewrite the sorting logic to be portable across both macOS (BSD) and Linux (GNU) without using GNU-specific extensions? Use standard unix utilities if needed.
```
**Outcome:** accepted — the AI refactored the logic to print unsorted counts prefixed with a label, then piped them through standard `sort` in the shell wrapper. This works perfectly on both macOS and Linux.
