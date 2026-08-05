# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This directory (`tier-1-warmup`) is one assessment exercise inside a larger multi-tier `AI-Assessment` repo (the actual git root is the parent directory; `git rev-parse --show-toplevel` will point there even when working from here). It is not an application codebase — it's a graded exercise scaffold. The task is defined in [README.md](README.md):

> Build a CLI/script that reads a CSV of engineers (`name,email,course_status`) from [data/engineers.csv](data/engineers.csv) and outputs (a) a count per status, and (b) the emails with status `pending` written to `pending.txt`. The input CSV may contain imperfect rows (missing/blank `course_status`, etc.) that must be handled gracefully rather than crashing.

## Expected deliverable layout

Solutions must go in a `solution/` subfolder (create it if missing) containing:

- `solution.py` (or equivalent) — runnable from the command line, e.g. `python solution/solution.py`
- `PROMPT_LOG.md` — every prompt sent to the AI, in order, plus a Tool & Workflow Note
- `VERIFICATION_NOTE.md` — 5–8 lines on what the AI got wrong and how correctness was verified

Templates for the last two live at `../templates/PROMPT_LOG.md` and `../templates/VERIFICATION_NOTE.md` (relative to this directory) — copy from there rather than inventing a new format. The root-level `PROMPT_LOG.md` and `VERIFICATION_NOTE.md` in this directory are blank/template copies, not the actual deliverable; the real ones belong inside `solution/`.

Grading (see README.md's rubric) weighs three things equally: whether the code handles edge cases, whether prompts show iterative refinement rather than one-liners, and whether verification actually caught an AI mistake — don't skip writing a real `VERIFICATION_NOTE.md`.

## Session logging via hooks (`.claude/`)

This repo has its own Claude Code hooks (`.claude/settings.json`) that auto-generate a `session-log.md` at the repo root as you work — this is separate from `PROMPT_LOG.md`, which is written by hand as a deliverable:

- **`UserPromptSubmit`** → [.claude/hooks/capture-prompt.sh](.claude/hooks/capture-prompt.sh) stashes each prompt to `.claude/logs/.pending/<session_id>.json`.
- **`Stop`** → [.claude/hooks/log-entry.sh](.claude/hooks/log-entry.sh) pairs the stashed prompt with the last assistant message, makes a *separate* headless `claude -p` call (with hooks disabled via `.claude/hooks/no-hooks.json`, to avoid recursive triggering) to draft Highlights/Limitations/Follow-up fields, and appends a `## Prompt N` section to `session-log.md`.
- `session-log.md` and `.claude/logs/.pending/` are gitignored — they're a local working log, not a deliverable. Don't hand-edit `session-log.md`'s generated entries; the `/context` block inside each is intentionally left for manual paste-in.
- These hooks make one extra `claude -p` subprocess call per turn — expect added latency/cost, and don't be surprised by a `session-log.md` appearing that you didn't create directly.

## Project-level skills (`.claude/skills/`)

Two skills are scoped to this repo:

- **`commit`** — drafts Conventional Commits-formatted messages from the staged diff and commits only after approval; prefer this over ad hoc `git commit` when asked to commit work here.
- **`draft-pr`** — opens a **draft** PR via `gh pr create` (never the raw API), always asking for base-branch confirmation and approval of title/body before creating anything.

Both require explicit user approval before their side-effecting step (commit / PR creation) — don't shortcut that when invoked.

## Working with `data/engineers.csv`

The sample file intentionally includes malformed rows to test edge-case handling: a row with a trailing empty `course_status` (`Marco Rivera,marco.rivera@example.com,`) and a row missing the column entirely (`Isabel Vargas,isabel.vargas@example.com`). Any solution must not crash on these and should decide/document how they're categorized (e.g. as `unknown`/`missing`) rather than silently dropping them.
