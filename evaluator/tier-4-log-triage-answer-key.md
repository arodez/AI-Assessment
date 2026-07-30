# Tier 4 (Agent Skill) — Log triage answer key

**DO NOT DISTRIBUTE TO CANDIDATES.** This is the measuring stick for `data/app.log` and for grading `TEST_LOG.md`.

---

## Planted clusters in `data/app.log` (539 lines, generated deterministically)

| # | Cluster | Rows | Symptom | Root cause |
|---|---------|------|---------|-----------|
| C1 | Deploy / config-change event | 121–122 | `inventory-sync-worker` v2.4.1 deploy completes; a WARN immediately follows noting `DB_CONNECTION_RELEASE_TIMEOUT_MS` is missing from the new release's env, falling back to "release-on-GC" (no explicit release) | This is the origin event — everything downstream traces back to it |
| C2 | Connection leak escalation (**true root cause**) | 129–523 (35 entries: WARN "checked out but not released" escalating to ERROR "pool exhausted" with tracebacks from ~row 300 onward) | `inventory-sync-worker`'s `sync_inventory_batch` holds connections from `shared_db_pool` for increasingly long periods (`held_for` climbs from ~30s to 130s+ across the file) and eventually fails to acquire new ones | Direct consequence of C1: without an explicit release timeout, leaked connections accumulate in the pool instead of being returned |
| C3 | DB timeout cluster (**the symptom — matches the candidate's example hypothesis**) | 157–530 (23 ERROR entries across `payment-service` and `api-gateway`, plus a `payment-service` FATAL at row 525) | `payment-service` and `api-gateway` — services that made no code or config change of their own — start failing with `ConnectionPoolTimeout` / `PoolExhaustedError` against the same `shared_db_pool` | Not an independent DB problem. These services share the pool with `inventory-sync-worker` (see rows 2–3 vs. row 5: all three connect to the same `shared_db_pool`); they're starved by C2, not failing on their own |
| C4 | Distractor cluster (unrelated) | 66–452 (12 WARN entries) | `auth-service` logs repeated rate-limit throttling for a few client IDs | Genuinely unrelated: `auth-service` uses a separate `session_store` (Redis, row 6), not `shared_db_pool`. It starts *before* the deploy (row 66 is at 09:05, deploy is at 09:14–09:15) and is present throughout at a steady rate — no causal link to C1/C2/C3 |

**Timing confirms the causal order:** C1 (09:14:58) → C2 begins 74 seconds later (09:16:12, row 129) → C3 begins ~6 minutes after C2 starts, once the pool is meaningfully depleted (09:20:47, row 157) → both C2 and C3 continue in parallel through the end of the file, culminating in the `payment-service` FATAL at row 525 (09:46:40). C4 runs on its own independent, unrelated timeline throughout.

## Expected output on the worked example query

> Query: *"there was an error in production, seems to be something related to timeouts to the database / db rejected connections, etc"*

A **shallow** skill (keyword search only) stops here:

```
Database related (your initial thought):
- [rows 157-530] ConnectionPoolTimeout / PoolExhaustedError across payment-service, api-gateway
  — DB connection pool exhausted — possible root causes: too much load, undersized pool
```

That's C3 only, framed as if it's the whole story — this is "Meets" at best on Root-cause reasoning (finds the hypothesized cluster, doesn't investigate further), and should not score above the middle of that rubric row.

A **well-designed** skill traces the pool exhaustion back further and reports something close to:

```
I found these instances of errors in the log:

Database related (your initial thought):
- [rows 157-530] ConnectionPoolTimeout / PoolExhaustedError across payment-service and
  api-gateway (23 occurrences, escalating, ending in a payment-service FATAL at row 525)
  — both services share `shared_db_pool` with inventory-sync-worker — possible root cause:
  pool starvation, not an independent DB issue.

Likely actual root cause (upstream of the DB errors above):
- [rows 121-122] inventory-sync-worker deployed v2.4.1 at 09:14:58; immediately logs a WARN
  that DB_CONNECTION_RELEASE_TIMEOUT_MS is missing from the new release's config, falling
  back to release-on-GC.
- [rows 129-523] Starting ~1 minute later, inventory-sync-worker repeatedly logs connections
  "checked out but not released," with held time climbing from ~30s to 130s+, eventually
  failing to acquire connections itself — consistent with a leak introduced by the v2.4.1
  config regression.
- This lines up with the DB cluster above starting ~6 minutes after the deploy, once enough
  connections had leaked to starve the shared pool.

Unrelated:
- [rows 66-452] auth-service rate-limit throttling warnings — separate store (Redis session
  cache, not shared_db_pool), present before the deploy and throughout at a steady rate. Not
  connected to the incident.
```

Exact wording will vary — grade the *behavior* (finds C3, correctly labels it as the stated hypothesis, traces to C2/C1 as the more likely actual cause, and doesn't misattribute C4), not phrasing.

## Grading notes — common false positives / shallow patterns

- **Keyword-search only:** returns every line containing "timeout," "error," "database," etc. without clustering — this is not triage, cap "Root-cause reasoning" at Below.
- **Confirms and stops:** finds C3, correctly describes it, never looks upstream — this is the expected "Meets" ceiling, not "Exceeds."
- **Fabricated row numbers:** cites rows that don't correspond to real content in `app.log` — treat like an AI-hallucinated bug elsewhere in this repo: a red flag, not a minor deduction.
- **Misattributes C4:** includes the `auth-service` distractor as part of the incident, or as a root cause — indicates the skill isn't actually distinguishing correlation from relevance.
- **`TEST_LOG.md` reads reconstructed:** run 1 output already looks like the "good" answer, or the "finding" in run 1 is suspiciously well-articulated for something that was supposedly a first attempt — a real first run on this log is unlikely to nail the upstream cause without being told to look for it.

## Evaluator checklist (~15–20 min)

1. **(3 min) Read `SKILL_BRIEF.md`.** Confirm it was plausibly written before `SKILL.md` (references the trigger/non-goals in the abstract, not "the skill does X" in a way that describes an already-built thing). Non-goals should include something like "does not attempt to fix the underlying issue."
2. **(5 min) Scan `SKILL.md` for tool-specific leakage.** Grep it for the candidate's own tool name, "Bash," "Grep," "MCP," or other agent-specific terms — a portable skill describes capabilities generically ("search the file," "read surrounding lines"), not by tool name. Confirm the adapter file is genuinely thin (a handful of lines pointing at `SKILL.md`) and doesn't re-embed the procedure.
3. **(5 min) Read `TEST_LOG.md`** against the four required parts (run 1 output, findings, fix, run 2 output + comparison). Cross-check the row numbers claimed in both runs against the table above. Confirm run 2 is genuinely different from run 1, not just re-pasted, and that the written comparison correctly explains why it's better.
4. **(5 min, optional) Re-run the skill live** if you have access to the candidate's tool — trigger it via the adapter with the worked-example query and compare against "Expected output" above.
5. **(2 min) Read `PROMPT_LOG.md` / `VERIFICATION_NOTE.md`** for the mandatory Tool & Workflow Note and general iteration signal, same as other tiers.

**Red flags:** `SKILL.md` reads like an implementation doc for one specific tool; `TEST_LOG.md` shows only one run or two runs with no meaningful difference; the brief's non-goals section is missing or generic; row numbers in `TEST_LOG.md` don't correspond to anything in `data/app.log`.
