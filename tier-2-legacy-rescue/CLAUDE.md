# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This repository holds a single inherited script, [`report_generator.py`](report_generator.py), which produces a weekly training-compliance report from a CSV export of engineers and their training status. The original author is no longer available, there is no test suite, and no documentation — the script "mostly works" but is known to produce wrong numbers and to crash on some inputs.

The task in this repo is to rescue the script: understand it, find and document its defects, add regression tests that fail against the original and pass against a fix, and ship a corrected, readable replacement — without changing its external behavior or CLI contract.

## Commands

The script has no external dependencies (only `sys` and `csv` from the standard library).

```bash
# Run the original script (read-only reference — do not modify)
python3 report_generator.py data/sample_input.csv /tmp/report.txt

# Run the corrected script (once solution/report_generator_fixed.py exists)
python3 solution/report_generator_fixed.py data/sample_input.csv /tmp/report.txt

# Run the test suite (pytest is not preinstalled — `pip install pytest` first)
python3 -m pytest solution/test_report_generator.py -v

# Run a single test
python3 -m pytest solution/test_report_generator.py::test_name -v
```

There is no linter, formatter, or CI configuration in this repo currently.

## Working rules for this repo

- **Never modify `report_generator.py`.** It is the reference implementation used to prove that new tests actually catch the original bugs (tests must fail against it and pass against the fix). All new work goes in a `solution/` directory.
- **Preserve the CLI contract.** The fixed script must be invocable exactly as `python report_generator_fixed.py <input.csv> <output.txt>` and must preserve all behavior that isn't an identified bug.
- **Every claimed defect must be reproduced**, not just asserted — back it with a failing test or a demonstrated run against `report_generator.py` before writing it up.
- Deliverables belong in `solution/`: `ANALYSIS.md`, `BUGS.md` (symptom / root cause / fix per defect), `test_report_generator.py`, `report_generator_fixed.py`, `PROMPT_LOG.md`, `VERIFICATION_NOTE.md`. Templates for the last two live at [`../templates/PROMPT_LOG.md`](../templates/PROMPT_LOG.md) and [`../templates/VERIFICATION_NOTE.md`](../templates/VERIFICATION_NOTE.md).

## Architecture of `report_generator.py`

A single-file, four-function script with no classes and a module-level global (`SKIPPED`):

1. `load_engineers(path)` — reads the CSV, skips the header row, and builds a list of dicts (`name`, `email`, `team`, `status`, `deadline`) by **positional** column index (`row[0]`..`row[4]`), not by header name. Rows that raise during parsing are meant to be caught and counted in `SKIPPED`, then skipped.
2. `count_by_status(engineers)` — tallies engineers into `completed` / `pending` / `in_progress` buckets by exact string match.
3. `overdue(engineers, today=...)` — returns emails of engineers who are not `completed` and whose `deadline` string is lexicographically less than `today` (string comparison, not date parsing — depends on `deadline` always being a zero-padded `YYYY-MM-DD` string to sort correctly).
4. `main()` — wires the above together and writes a plain-text report to the output path: header line, per-status counts, skipped-row count, then a bulleted list of overdue engineers' emails.

Data flow: CSV rows → list of engineer dicts → (status counts, overdue list) → flat text report. There is no schema validation beyond the try/except in `load_engineers`, and no date normalization — both are relevant when reasoning about malformed input.

`data/sample_input.csv` is written to exercise messy real-world input, not just the happy path: mixed-case status values, a value with trailing whitespace, a non-zero-padded date, and a short row missing trailing columns. Use it (and hand-crafted variants) to reproduce defects before writing tests against them.

## Session logging (automatic)

Hooks under `.claude/hooks/` are wired in `.claude/settings.json` and run automatically during Claude Code sessions in this repo — no action is needed to trigger them:

- `capture-prompt.sh` / `log-entry.sh` append a per-prompt entry (timestamp, model, mode, a Claude-drafted highlights/limitations/follow-up summary) to a `session-log.md` at the repo root as the session progresses.
- `protect-branches.sh` blocks `git push` from targeting the `main` or `JavierCA_Solution` branches directly (including sweeping pushes via `--all`/`--mirror`); push a feature branch instead.
