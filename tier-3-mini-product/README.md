# Tier 3 — Mini product with an agentic workflow

**Time box:** 1 day (8 working hours max) · **Points:** 100

⚠️ **This tier requires its own fresh git repository** — commit history is graded. Do not work inside this assessment repo.

## Scenario

The L&D team needs a small internal web app: the **Training Compliance Dashboard**. It ingests a CSV of engineers and training statuses and gives managers visibility plus a way to draft reminder messages. You must build it **primarily through an agentic AI workflow** (Cursor agent, Windsurf Cascade, Copilot agent mode, Claude Code, or Replit).

A sample dataset is provided at [`data/training_data.csv`](data/training_data.csv).

## Functional requirements

1. **Ingest** — upload/load a CSV (`name,email,team,course,course_status,deadline`). Validate it and report rejected rows to the user — never silently drop data.
2. **Dashboard** — completion percentage per team and per course; list of engineers overdue (status not `completed` and deadline in the past).
3. **Reminders** — for any overdue engineer, generate a polite reminder message (template-based or AI-generated — your choice; if AI-generated, the API key must not be hardcoded).
4. **Persistence** — the last uploaded dataset survives a restart (file or SQLite; no external DB required).

## Engineering requirements

1. **Conventions file first** — before generating code, create a rules/instructions file for your tool (e.g., `.cursor/rules`, `copilot-instructions.md`, `CLAUDE.md`) defining stack, naming, error-handling, and testing conventions. **Commit it first.**
2. **Version control** — meaningful incremental commits (≥10). A single "initial commit" with the whole app scores zero on the workflow criterion.
3. **Tests** — automated tests for the ingestion/validation logic and the overdue calculation (the two highest-risk areas). UI tests not required.
4. **Security pass** — no secrets in the repo (check your history!); input validation on upload; a brief note on what you checked.
5. **README** — setup, run, test instructions; architecture in ≤5 sentences; known limitations.

## AI-usage report (1 page, required — `AI_USAGE.md`)

- Which workflow modes you used where (agent vs chat vs inline) and why.
- Two examples where you rejected or corrected AI output, with evidence.
- What you would **not** trust the agent to do unsupervised in a client repo.

## Constraints

- Stack is free choice (Flask, FastAPI, Node/Express, etc.) — judged on working software, not framework.
- Time box: 8 working hours. **Unfinished is acceptable; undocumented is not.** Cut scope consciously and say so in the README.

## Deliverables

A link to your repo containing the app plus `AI_USAGE.md`, `PROMPT_LOG.md`, and `VERIFICATION_NOTE.md` (templates in [`../templates/`](../templates/)).

## Rubric (100 pts)

| Criterion | Pts | What "Meets" looks like |
|---|---|---|
| Working software | 25 | Requirements 1–2 fully work; 3–4 at least partially; app runs from README instructions alone |
| Data correctness | 15 | Overdue logic uses real date comparison; rejected rows surfaced; totals verifiable against a hand-checked sample |
| Agentic workflow quality | 20 | Conventions file exists and is reflected in the generated code; commit history shows incremental, reviewed agent-driven work |
| Tests | 15 | Ingestion + overdue logic covered; tests pass; at least one test catches a case the AI initially got wrong |
| Security & robustness | 10 | No secrets committed; upload validated; security note credible |
| AI-usage report & prompt log | 15 | Honest, specific, shows judgment about when NOT to trust the agent |
