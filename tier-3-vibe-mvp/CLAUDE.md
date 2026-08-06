# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This repository currently holds only the product specification for the **Community Events Hub** — no application code exists yet. The MVP itself, and all supporting docs, must live under a top-level `solution/` folder that does not exist yet and needs to be created as the first step of implementation. Once that scaffolding is in place, update this file with the real build/lint/test commands and the actual architecture — the guidance below describes the target, not what's on disk today.

## What's being built

Community Events Hub: an internal mini-app for publishing events (study groups, AMAs, workshops) and letting people RSVP. Required functionality:

1. **Create event** — title, date, description, maximum capacity.
2. **Sign-up (RSVP)** — valid email required, no duplicate sign-ups per event, clear rejection once an event is full.
3. **Public list** — upcoming events sorted by date, showing remaining spots.
4. **Organizer view** — attendee list per event, exportable (CSV or copy).

Persistence can be in-memory for the MVP as long as that limitation is documented; file-based or SQLite storage is a plus. Stack is otherwise unconstrained.

## Required project documents

These live alongside the app under `solution/` and are as much a part of the deliverable as the code:

- `BRIEF.md` — the complete product brief, written *before* any code is generated: what's being built, for whom, requirements, technical constraints, edge cases, and acceptance criteria.
- `PROMPT_LOG.md` — the record of prompts used to drive implementation, showing real iteration (corrections, not just a clean first pass).
- `SECURITY_CHECK.md` — a documented security pass covering at minimum: no secrets/API keys in code, input validation (malformed email, negative capacity, empty title, etc.), and no unintended data exposure (e.g. one attendee seeing another's email via the public list).
- `VERIFICATION_NOTE.md` — documented manual verification of at least three flows: successful sign-up, rejection when an event is full, rejection of a duplicate email — including at least one real mistake caught along the way.
- `solution/README.md` — startup instructions sufficient to run the app from a clean checkout.

Templates for `PROMPT_LOG.md` and `VERIFICATION_NOTE.md` are available in `../templates/`.

When implementing, write `BRIEF.md` first and keep `PROMPT_LOG.md` current as work progresses — don't reconstruct it after the fact.

## Git workflow

`main` and `JavierCA_Solution` are protected: a pre-push hook (`.claude/hooks/protect-branches.sh`) blocks direct pushes to either. Work on a feature branch and open a PR instead.
