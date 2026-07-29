# Prompt Log

> Record **every** prompt sent to the AI, in order, unedited. Add a one-line note on what you did with the response (accepted / modified / rejected). Exported chat links or screenshots may be attached instead, but the accept/modify/reject notes are still required.

## Tool & Workflow Note

**Tool used:** Claude Code (Sonnet 5)
**Mode(s) used:** agent (plan mode for scoping, then agent mode for execution — single continuous session, no inline/autocomplete usage)
**Notable limitations or surprises:** The AI's first read of `report_generator.py` correctly spotted the mutable-default-argument and dead-code-after-`continue` bugs on inspection alone, but the case/whitespace status bug and the non-zero-padded-date overdue bug were only confirmed as *real* (not just theoretically possible) by actually running the original script against `data/sample_input.csv` and diffing the buggy output against hand-computed expected values — inspection alone wasn't sufficient evidence. The AI also initially proposed keeping `overdue()`'s `today` string comparison "mostly as-is" and only parsing when needed; this was tightened to parse both sides into `datetime.date` up front for a cleaner, obviously-correct fix.

---

### Prompt 1
**Mode:** agent (plan mode)
```
this repo is a collection of 5 tests to asses the use of AI for coding.

currently we are gonna work in this folder tier-2-legacy-rescue

Your job is to read the @tier-2-legacy-rescue/README.md  file, understand the test it is giving and prepare a plan to present all the deliverable its asking for.

You will only act with the folders and files inside tier-2-legacy-rescue and the templates folder above it, do not go into other folders since they are other unrelevant tests.

Ask any questions that you need to comple the task.
```
**Outcome:** accepted — read `README.md`, `report_generator.py`, `data/sample_input.csv`, and the two `templates/` files; independently traced the code to identify 4 candidate bugs (mutable default arg, dead `SKIPPED` increment after `continue`, case/whitespace-sensitive status matching, string-compared non-zero-padded dates) before writing them into a plan. No open ambiguity was found worth blocking on, so no clarifying questions were asked — plan was written directly and approved as-is.

### Prompt 2
**Mode:** agent (execution, after plan approval)
```
[Plan approved via ExitPlanMode UI — no additional free-text instructions given]
```
**Outcome:** accepted — proceeded to implement the approved plan: reproduced all 4 bugs by running the original script and isolated function calls, wrote `ANALYSIS.md`/`BUGS.md`/`report_generator_fixed.py`/`test_report_generator.py`, ran the test suite against both the fixed module (6/6 pass) and a throwaway copy of the original under the fixed module's name (5/6 fail, confirming each targeted a real bug), then wrote this log and `VERIFICATION_NOTE.md`.

### Prompt 3
**Mode:** agent (chat, post-implementation)
```
rewrite your summary but in a comparison format, for example:
Readme file called for:
Find the bugs — the script contains 4 planted defects (logic, data handling, and robustness). Identify at least 3. Document each in BUGS.md: symptom, root cause, fix.
- My BUGS.md is correct because I wrote 4 bugs, each with a real reproduction: mutable default arg (state leaks across calls), dead SKIPPED counter (unreachable code after continue), case/whitespace-sensitive status matching, string-compared non-zero-padded dates
```
**Outcome:** accepted — restated the completion summary as a requirement-by-requirement comparison (each README ask paired with the corresponding deliverable and evidence), no changes to any solution files.

### Prompt 4
**Mode:** agent (chat, post-implementation)
```
add this last bit to the @tier-2-legacy-rescue/solution/PROMPT_LOG.md so that it stays up to date
```
**Outcome:** accepted — appended Prompt 3 and this prompt to the log to keep it a complete, in-order record.
