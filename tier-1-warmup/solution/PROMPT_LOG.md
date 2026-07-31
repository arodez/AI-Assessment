# Prompt Log

> Record **every** prompt sent to the AI, in order, unedited. Add a one-line note on what you did with the response (accepted / modified / rejected). Exported chat links or screenshots may be attached instead, but the accept/modify/reject notes are still required.

## Tool & Workflow Note

**Tool used:** Antigravity (Gemini)  
**Mode(s) used:** agent  
**Notable limitations or surprises:** None. The assistant successfully checked the repository structure, asked for clarification on the target directory path, and created the file.

---

### Prompt 1
**Mode:** agent
```
I want to create a PROMPT_LOG.md file, under the folder tier-1-warmup, using the template and indications inside  @[templates/PROMPT_LOG.md] 
```
**Outcome:** accepted — The tool asked for directory preference and generated the template file.

### Prompt 2
**Mode:** agent
```
I want to create a PROMPT_LOG.md file, under the folder tier-1-warmup, 
Record **every** prompt sent to the AI, in order, unedited. Add a one-line note on what you did with the response (accepted / modified / rejected). Exported chat links or screenshots may be attached instead, but the accept/modify/reject notes are still required.
 Record: **Tool used:** (e.g., GitHub Copilot, Cursor, ChatGPT, Windsurf, Replit)  
**Mode(s) used:** (chat / inline / agent — list all that apply)  
**Notable limitations or surprises:** (what the tool got wrong, refused to do, or surprised you with — "none" is rarely true)
Log in this format: ### Prompt 1
**Mode:** (chat / inline / agent)
```
<paste prompt here>
```
**Outcome:** accepted / modified / rejected — because…
```
**Outcome:** accepted — The tool updated the prompt log with the history of the conversation.

### Prompt 3
**Mode:** agent
```
I need create a python script (solution.py), that read CSV file as input with name , email, course_status, nd outputs: (a) the count per status, and (b) a list of emails with status "pending", written to pending.txt.

Validate the input, and if necesary handle the errors
```
**Outcome:** accepted — The tool created solution.py with CSV parsing, header verification, status counting, validation logic (skipping invalid rows/emails/statuses), and written output to pending.txt.

### Prompt 4
**Mode:** agent
```
Add a line informing the script starts and finish, also include some unit test, for the common errors like missing file, invalid column format, missing data and for invalid email
```
**Outcome:** accepted — The tool added start/finish print banners, refactored process_csv and write_pending into testable functions, and created test_solution.py with 18 unit tests covering: missing file, empty file, invalid/missing columns, empty name/email/status, too-few columns, invalid email, happy path, and write_pending output. All 18 tests pass.

### Prompt 5
**Mode:** agent
```
validate why if i put on the csv a line with '','','' there is no error found, fix it and add a test for that scenario
```
**Outcome:** accepted — The tool identified the root cause (a single `if not row or all(...)` guard that silently skipped whitespace-only rows), split it into two branches so all-whitespace rows now emit a warning to stderr, and added 3 new tests (skipped-not-counted, warning printed, empty-counts) under TestProcessCSVWhitespaceOnlyRow. All 21 tests pass.

### Prompt 6
**Mode:** agent
```
please correct the process when there are more columns than the required ones, ignore the non-required to avoid skipping for the max_idx validation, also add the tests
```
**Outcome:** accepted — The tool replaced the single max_idx check with a per-required-column validation using a list comprehension, so extra non-required columns in the header or trailing values in data rows are ignored. Error messages now name the specific missing column(s). Added 4 new tests under TestProcessCSVExtraColumns covering trailing header columns, trailing data values, non-required column between required ones, and specific column name in error message. All 25 tests pass.

