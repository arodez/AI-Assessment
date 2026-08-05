# Verification Note

**1. What the AI got wrong (or almost wrong):**
- The initial plan proposed `python = "^3.11"` in `pyproject.toml`. I corrected it to `^3.14` during plan review before implementation started.
- I didn't expect that the `/init` command also takes the purpose of logging the prompts and generating the verification note, which could help in some cases, but I was expecting to do the exercise the most real-scenario possible, like within a client's project, not as part of an evaluation tool.
- Markdown templates taken from the incorrect directory, I customized the templates and add the new version into the current folder, it took the parent (original) ones even after I modified it in the `PLAN.md` document.
- A commit action took more time than expected, I thought it was already expecting for my response.

**2. How I caught it:**
- The Python version issue was caught by reading the Explore agent's environment report (only Python 3.14.6 present, no pyenv) against the proposed constraint before approving the plan.
- I didn't correct the Markdown templates since the generated ones by Claude Code were useful, but I had to mix and correct the path before opening the draft PR.
- The UI marked a new prompt as unread and that it was still thinking about the previous step (committing) when all the commits were already completed and the UI asked a question which made it confusing.

**3. How I confirmed the final result is correct:**
- Ran `poetry run pytest -v` — all 35 tests pass, including a regression test asserting exact counts (10 total, 3 pending/3 completed/2 in_progress/2 unknown) against the `data/engineers.csv` example file.
- Separately ran the CLI manually against that same file (`poetry run python solution.py ../data/engineers.csv`) and hand-verified the stdout counts and the generated `pending-*.txt` contents (exactly the 3 expected emails, correct order) against numbers computed by eye from the CSV. Also manually exercised `--help` and the missing-file error path to confirm exit codes and messages behave as documented in `GUIDE.md`.
