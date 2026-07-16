# Prompt Log

> Record **every** prompt sent to the AI, in order, unedited. Add a one-line note on what you did with the response (accepted / modified / rejected). Exported chat links or screenshots may be attached instead, but the accept/modify/reject notes are still required.

## Tool & Workflow Note

**Tool used:** Windsurf
**Mode(s) used:** Chat & Inline Edit
**Notable limitations or surprises:** 
1. The AI hallucinated two false-positive bugs (claiming `engineers or []` was a bug and that `csv.DictReader` was required with `newline=''`).
2. When refactoring the mutable default argument in `append_row(row, rows=[])`, the AI fixed the function definition but forgot to update the call site in `load_engineers` to pass the accumulated list. This would have caused the script to only return a list containing the very last row.

---

### Prompt 1
**Mode:** Chat
```
Please analyze report_generator.py and describe what it does, its inputs and outputs, and its high-level structure.
```
**Outcome:** Accepted — The AI's summary of the script's core purpose, input/output structures, and functions was accurate and was used to build `ANALYSIS.md`.

### Prompt 2
**Mode:** Chat
```
Can you identify the bugs in report_generator.py? Explain what is wrong and how they manifest.
```
**Outcome:** Modified — The AI correctly identified B1 (mutable default argument), B2 (case/whitespace matching), B3 (lexicographical date comparison), and B4 (dead skip counter after continue). However, it also claimed that `engineers or []` was a bug and that `csv.DictReader` was required. I rejected these false positives and documented only the 4 real bugs in `BUGS.md`.

### Prompt 3
**Mode:** Chat
```
Write automated tests using pytest for test_report_generator.py that verify these 4 bugs are fixed in report_generator_fixed.py.
```
**Outcome:** Modified — The AI wrote a good baseline of tests, but did not handle the resetting of the global `SKIPPED` variable between tests, which caused state to leak between tests. I modified the code to manually reset `report_generator_fixed.SKIPPED = 0` at the start of each file-load test.

### Prompt 4
**Mode:** Inline Edit
```
Refactor report_generator.py into report_generator_fixed.py, fixing all 4 bugs, adding type hints and docstrings, and keeping the CLI behavior exactly the same.
```
**Outcome:** Modified — The AI refactored `append_row(row, rows=None)` to use `None` as the default argument. However, it called it as `engineers = append_row({...})` inside `load_engineers` without passing the second argument. This would result in the accumulation list never being passed down, returning only the last row. I modified the code to pass `engineers` as the second argument: `engineers = append_row({...}, engineers)`.
