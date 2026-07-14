# Applied AI for Coders — Practical Assessment

Hands-on assessment for the **Applied AI for Coders** track (DataCamp). It verifies that you can *apply* AI-assisted development skills — prompting, tool workflows, and verification — not just recall concepts.

Any AI assistant is allowed (GitHub Copilot, Cursor, Windsurf, Claude, ChatGPT, Replit). **The workflow is what is evaluated, not the tool.**

## Structure

| Tier | Folder | Time box | Focus |
|---|---|---|---|
| 1 — Warm-up script | [`tier-1-warmup/`](tier-1-warmup/) | 25 min | Basic prompting, happy-path verification |
| 2 — Legacy rescue | [`tier-2-legacy-rescue/`](tier-2-legacy-rescue/) | 1–2 hours | Code comprehension with AI, testing, refactoring, bug hunting |
| 3 — Mini product | [`tier-3-mini-product/`](tier-3-mini-product/) | 1 day (8 h max) | Agentic workflow, conventions, multi-file work, security, delivery |

## Universal deliverables (all tiers)

Every tier requires the same three artifacts:

1. **Final code** — working, runnable from your instructions.
2. **Prompt log** — every prompt sent to the AI, in order, unedited. Use [`templates/PROMPT_LOG.md`](templates/PROMPT_LOG.md). Exported chats or screenshots are also fine.
3. **Verification note** — what the AI got wrong, how you caught it, and how you confirmed correctness. Use [`templates/VERIFICATION_NOTE.md`](templates/VERIFICATION_NOTE.md).

## How to submit

1. Fork or copy this repo (or create a fresh repo per tier — Tier 3 **requires** its own repo with real commit history).
2. Work inside the tier folder. Keep the prompt log as you go — reconstructing it afterwards never works.
3. Share the repo link (or a zip) with your evaluator.

## Ground rules

- AI assistance is **expected and required** — using it well is the whole point.
- Everything the AI claims, you verify. Reporting an AI-hallucinated "bug" or shipping unverified code counts **against** you.
- Time boxes are honest limits. Unfinished is acceptable; undocumented is not.

## For evaluators

Grading materials (planted-bug keys, review protocols, trap datasets) live in [`evaluator/`](evaluator/). **Do not distribute that folder to candidates** — when publishing this repo for a cohort, delete `evaluator/` or keep it in a separate private repo.
