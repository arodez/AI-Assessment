# Tier 4 — Agent Skill Builder

**Time box:** 2–3 hours · **Points:** 100

## Task

The other tiers test whether you can drive an AI assistant to build software. This one tests something narrower and increasingly relevant: can you **package a repeatable capability as a skill the agent can invoke on its own**, instead of re-explaining the same task in a fresh prompt every time?

There is no app to ship here — no UI, no persistence. Your deliverable is a small, well-scoped piece of agent tooling, plus evidence that you understood the problem and iterated on your own design.

**Grading philosophy — read this before you start:** we are not grading whether your skill is clever or polished. We're grading whether you scoped it sensibly, wrote instructions an agent could actually follow, and — this is the part most candidates will be tempted to skip — **actually ran it, found it lacking, and fixed the instructions.** A submission where everything worked perfectly on the first try, with no evidence of a real failure and fix in `TEST_LOG.md`, will not score full marks. That reads as untested, not excellent — the same way a `VERIFICATION_NOTE.md` claiming "the AI made no mistakes" is a red flag elsewhere in this repo.

## Scenario

You're building a **log triage skill**: given a natural-language query describing a suspected production incident, it searches a log file and returns a structured diagnosis — not just a list of every error line, but a clustered, explained answer.

A sample log is provided at [`data/app.log`](data/app.log). Treat it the way you'd treat a real incident: you don't know in advance what's in it.

Here's the worked example your skill should handle:

> **Query:** "there was an error in production, seems to be something related to timeouts to the database / db rejected connections, etc"
>
> **Expected shape of response:**
> ```
> I found these instances of errors in the log:
>
> Database related (your initial thought):
> - [row(s) N–M] <top of stack trace> — <quick description> — possible root causes: ...
>
> <other relevant cluster(s), if the evidence points elsewhere or upstream>
> - [row(s) ...] <top of stack trace> — <quick description> — possible root causes: ...
> ```

Two behaviors matter more than the exact formatting:

1. **It has to find real evidence, with real row numbers**, not a vague paraphrase of the query.
2. **It must not just confirm your hypothesis.** A skill that only echoes back "yes, here are some DB errors" and stops there is doing keyword search, not triage. A good skill independently clusters what's actually in the log, explicitly tells you which cluster matches what you described, and flags anything else worth your attention — including the possibility that what you're looking at is a symptom of something else.

You will not be told in advance whether the log's real story matches the example hypothesis. Building and testing the skill honestly is how you find out.

## How the skill is packaged

Every candidate uses a different coding agent (Claude Code, Cursor, Windsurf, Copilot, Aider, whatever you work in day to day) — that's fine, that's the point. To keep the skill portable across agents rather than locked to your tool, build it as **two files**:

1. **`SKILL.md`** — the core instruction set, written in **platform-neutral language**. No tool names, no agent-specific jargon: don't write "use the Grep tool" or "invoke Bash," write "search the log file for..." or "read the matching lines and their surrounding context." Someone using a completely different agent should be able to read this file and reimplement your skill without ever seeing your native config. Structure it with:
   - A trigger description (when this skill should fire)
   - Required input(s)
   - An ordered procedure, in generic capability terms
   - The output format (matching the shape above)
   - Known limitations / edge cases
2. **A thin adapter** — a few lines in whatever native mechanism your tool actually uses (a Claude Code skill's frontmatter, a `.cursor/rules` entry, a Windsurf workflow stub, a Copilot custom-instructions pointer, an Aider convention file, etc.) whose only job is telling your agent *when to load* and *where to find* `SKILL.md`. The adapter should not duplicate the procedure — it delegates to `SKILL.md`.

**You must demonstrate this live, in your own agent** — actually trigger the skill through the adapter and capture the real output. A hand-written mock of what the output "would look like" does not count.

## Deliverables

No fresh repo needed for this tier — work inside a folder called `solution/` under `tier-4-agent-skill/` (same pattern as Tiers 1 and 2) and place the following in it (templates for the last two are in [`../templates/`](../templates/)):

- **`SKILL_BRIEF.md`** — written **before** `SKILL.md` exists: why this is a good candidate for a skill (a recurring, well-bounded task an agent won't reliably handle ad hoc), the trigger condition, explicit non-goals (e.g., "does not attempt to fix anything, only diagnose"), and your acceptance criteria for "this skill works."
- **`SKILL.md`** — the platform-neutral core, as described above.
- **The adapter file** — committed in its native location for whichever tool you used (e.g. `.claude/skills/...`, `.cursor/rules/...`), plus a one-line note in your submission saying which tool it targets.
- **`TEST_LOG.md`** — run the query above against `data/app.log` **twice**, and write up all four of these parts:
  1. **Run 1 output** — the actual captured output from your first live invocation.
  2. **Findings from run 1** — your own written assessment of what was wrong or shallow about it. Be specific: did it stop at the obvious cluster? Hallucinate a row number? Just agree with the hypothesis without checking anything else?
  3. **The fix** — what you changed in `SKILL.md`'s instructions to address the finding.
  4. **Run 2 output + comparison** — the actual captured output from the second invocation, and a short written explanation of *how it's better than run 1* and why that traces back to the fix you made.

  This is the highest-weighted deliverable. A flawless-looking first run is not a good sign — it usually means the gap wasn't found, not that there wasn't one.
- **`PROMPT_LOG.md`** and **`VERIFICATION_NOTE.md`** — same as every other tier, including the mandatory Tool & Workflow Note at the top of the prompt log.

## Rubric (100 pts)

A technically perfect skill with no visible failure or iteration in `TEST_LOG.md` should **not** score full marks — this tier grades whether you understood and iterated on the problem, not the polish of what shipped.

| Criterion | Pts | Exceeds | Meets | Below |
|---|---|---|---|---|
| Scenario understanding & brief | 15 | Clear non-goals, correctly identifies this as a recurring/bounded task worth packaging | Adequate brief, scope mostly reasonable | Vague, unscoped, or brief clearly written after the fact |
| Skill design & portability | 20 | `SKILL.md` has zero tool-specific leakage, adapter is genuinely thin, trigger condition precise | Mostly portable, minor leakage or a slightly bloated adapter | `SKILL.md` reads like it's tied to one tool; adapter duplicates the procedure |
| Root-cause reasoning in output | 20 | Skill correctly separates symptom from a deeper cause where the evidence supports it, doesn't just confirm the stated hypothesis | Finds the hypothesized cluster correctly but only partially investigates further | Only confirms the hypothesis, or returns unrelated noise |
| Testing & iteration (`TEST_LOG.md`) | 30 | Real failure on first run, concrete fix to the instructions (not just a re-run), clear before/after with a genuine comparison | Some gap shown and addressed, but thin | No real failure shown, or log reads as reconstructed after the fact |
| Prompt log & verification note | 15 | Iterative strategy visible, honest about AI mistakes at the meta (skill-writing) level | Complete, some iteration | Missing or single mega-prompt |
