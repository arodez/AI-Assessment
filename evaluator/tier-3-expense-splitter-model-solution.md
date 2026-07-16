# Tier 3 Variant B (Expense Splitter) — Reference solution & grading key

**DO NOT DISTRIBUTE TO CANDIDATES.**

---

## Prompt 1 — The optimal brief (what "Exceeds" looks like)

> I want to build a web app called **Trip Split** so a group of friends can track shared expenses during a trip and settle up at the end.
>
> **Users:** one shared view for the whole group — no accounts or login for the MVP.
>
> **Requirements:**
> 1. Add/remove participants by name (names must be unique, non-empty).
> 2. Add expenses: description (non-empty), amount (positive number, 2 decimals max), and payer (selected from participants — never free text).
> 3. Every expense is split equally among ALL current participants at the moment it's added, and the expense stores its own participant snapshot — adding someone later must NOT change past expenses.
> 4. Balances view: for each person, total paid minus fair share, always summing to zero across the group.
> 5. Settlement view: a minimal list of "X pays Y $Z" transfers that zeroes all balances (fewest transfers preferred, but correctness matters more than minimality).
> 6. Persist everything in localStorage; refreshing the page restores the trip. A "reset trip" button with confirmation.
>
> **Stack and constraints:** single-page vanilla HTML/CSS/JS (or React, your call) — no backend, no build step, one file I can open in a browser. Don't invent features I didn't ask for (no currencies, no receipts, no auth).
>
> **Money-handling rules:** store amounts in integer cents to avoid floating point errors. When a split doesn't divide evenly (e.g., $100 / 3), distribute the leftover cents deterministically (e.g., to the earliest participants) so the totals always reconcile to the exact expense amount.
>
> **Edge cases it must handle without breaking:** amount 0, negative, or non-numeric → rejected with a message; deleting a participant who has paid or owes → blocked with an explanation (settle first); expense added when only 1 participant exists.
>
> **Acceptance criteria:** with Ana, Bruno, Carla — Ana pays $300 hotel, Bruno pays $150 dinner, Carla pays $60 taxi — the app must show balances Ana +$130, Bruno −$20, Carla −$110, and a settlement of exactly: Carla → Ana $110, Bruno → Ana $20. After a page refresh, the same numbers are still there.
>
> Show me the data model and the settlement algorithm plan before generating the full code.

**Why it's optimal:** it resolves *in advance* the three decisions the AI would otherwise make silently — split snapshot vs. retroactive splitting, integer cents vs. floats, and blocked vs. cascading participant deletion. It also embeds a numeric acceptance test the candidate can verify by hand. That's requirement decomposition, which is exactly what this exercise claims to test.

## Typical optimal iterations (examples)

**Math correction:**
> The balances don't sum to zero: with $100 split among 3 people the app shows each owing $33.33, losing a cent. Here's the split function: [paste]. Switch the model to integer cents and assign the remainder cent(s) to the first participant(s) in order. Change only the split logic and show me the updated function plus the recalculated example.

**State/persistence audit:**
> Before I continue: list everything currently held in memory that would be lost on refresh, and confirm the localStorage write happens on every mutation (add/edit/delete), not just on some. Don't change code yet — just audit.

**Recalculation check (if attempting the edit/delete bonus):**
> I edited the hotel expense from $300 to $200 and the settlement view still shows the old transfers. Trace where settlement is computed and make it derive from current state on every render instead of being stored.

## Ground-truth test scenario (grading "Settlement correctness")

Enter exactly this in the candidate's app:

**Participants:** Ana, Bruno, Carla
**Expenses:** Ana pays 300.00 (hotel) · Bruno pays 150.00 (dinner) · Carla pays 60.00 (taxi)

**Expected output:**
- Total 510.00 → fair share 170.00 each
- Balances: **Ana +130.00 · Bruno −20.00 · Carla −110.00** (must sum to 0)
- Settlement: **Carla → Ana 110.00** and **Bruno → Ana 20.00** (2 transfers; any correct set that zeroes balances is acceptable, but >2 transfers here caps the criterion at "Meets")

**Rounding probe:** add a 4th expense — Bruno pays 100.00. New fair share = 610/3 = 203.33̄.
- Acceptable: balances shown as Ana +96.67 · Bruno +46.67 · Carla −143.33 (or ±0.01 with the leftover cent assigned deterministically and totals reconciling).
- Failure: balances that don't sum to ~0, or a settlement that doesn't clear them. If the app shows 203.33 for everyone and silently loses the cent in totals, "Settlement correctness" caps at "Meets" low; if balances visibly contradict each other, it's "Below."

**Integrity probes (from the README's data-integrity questions):**
1. Amount `-50` or `0` → must be rejected, not corrupt balances.
2. Amount `abc` → rejected without breaking the page.
3. Delete Carla while she owes money → blocked with explanation, OR allowed with a documented, consistent recalculation. Undefined behavior (balances silently wrong) = fail this probe.
4. Refresh the page → all data intact (persistence requirement).

## Expected AI mistakes (what the verification note should catch)

The most common defects AI produces on this exact app — a credible `VERIFICATION_NOTE.md` will contain at least one of these:
- Floating point drift (0.1 + 0.2 style) making balances sum to 0.00000001 or −0.01.
- Settlement algorithm that pairs debtors/creditors but leaves a residual balance.
- New participant retroactively included in old expenses (or excluded inconsistently).
- localStorage written on add but not on delete/edit.
- Payer stored as free text, so "Ana" and "ana " become two people.

A note claiming "the AI made no mistakes" on this exercise is a strong signal the candidate didn't verify.

## Evaluator checklist (15 min)

1. Start the app from the candidate's README alone.
2. Enter the ground-truth scenario → check balances and settlement against the numbers above.
3. Run the rounding probe.
4. Run the 4 integrity probes.
5. Refresh → data intact.
6. Cross-check `PROMPT_LOG.md` against the code: do the iterations match what exists?
7. Check `BRIEF.md` against the 5-dimension rubric (money edge cases anticipated?).
8. Bonus, if claimed: unequal split verified with a hand calculation; edit an expense and confirm settlement recalculates.
