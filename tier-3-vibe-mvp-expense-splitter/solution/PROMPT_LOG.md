# Prompt Log

> Record **every** prompt sent to the AI, in order, unedited. Add a one-line note on what you did with the response (accepted / modified / rejected).

## Tool & Workflow Note

**Tool used:** GitHub Copilot (VS Code Agent Mode)  
**Mode(s) used:** Agent (chat-driven development with full file creation)  
**Notable limitations or surprises:** The AI initially used floating-point dollars for internal storage instead of integer cents, causing rounding drift. It also generated a settlement algorithm that didn't handle the case where debtors/creditors weren't sorted, leading to suboptimal (extra) transfers.

---

### Prompt 1 — Initial Brief
**Mode:** Agent
```
Build a single-page web app called "Trip Split" that helps friends split expenses on a trip. 
Requirements: add/remove participants, add expenses with description/amount/payer, split equally 
among all current participants, show balances, show settlement (who owes whom), persist in localStorage.
Stack: single HTML file, vanilla JS, no build step. Store amounts as integer cents to avoid 
floating-point issues. Handle edge cases: zero/negative amounts rejected, rounding with remainder 
distribution, participant deletion blocked if involved in expenses.
Acceptance test: Ana pays $300, Bruno pays $150, Carla pays $60 → balances +130, -20, -110, 
settlements Carla→Ana $110, Bruno→Ana $20.
```
**Outcome:** Accepted with modifications — the initial code used `parseFloat` for internal storage (dollars, not cents), which I caught immediately. See Prompt 2.

---

### Prompt 2 — Fix floating-point storage
**Mode:** Agent
```
The amount is stored as a float internally (e.g., 300.00). This will cause rounding drift when 
splitting $100 among 3 people — 33.33 * 3 = 99.99, losing a cent. Change the internal model to 
store ALL amounts as integer cents (multiply by 100 on input, divide by 100 only for display). 
The split function should use Math.floor for the base and distribute remainder cents to the 
first participants alphabetically. Show me the updated computeSplits function and the conversion utilities.
```
**Outcome:** Accepted — the AI rewrote the data model to use `amountCents` throughout and created `dollarsToCents()` / `centsToDollars()` helpers. Verified: $100 / 3 now produces splits of 34 + 33 + 33 = 100 cents correctly.

---

### Prompt 3 — Settlement algorithm produces extra transfers
**Mode:** Agent
```
With the test scenario (Ana +130, Bruno -20, Carla -110), the settlement shows 3 transfers 
instead of 2. The issue is the greedy algorithm isn't sorting debtors/creditors by amount 
before matching. Fix: sort both arrays descending by amount, then greedily match largest debtor 
with largest creditor. The expected result is exactly 2 transfers: Carla→Ana $110, Bruno→Ana $20.
```
**Outcome:** Accepted — sorted both `debtors` and `creditors` arrays descending before the matching loop. Verified with the acceptance test scenario: now produces exactly 2 transfers.

---

### Prompt 4 — Participant snapshot not stored per-expense
**Mode:** Agent
```
When I add a new participant AFTER existing expenses, those old expenses get recalculated to 
include the new person. This is wrong — the brief specifies that each expense stores a snapshot 
of who was present when it was created. Add a `splitAmong` array to each expense that captures 
the participants at creation time. The split calculation must use this snapshot, not the current 
participant list.
```
**Outcome:** Accepted — each expense now stores `splitAmong: [...state.participants]` at creation time. Adding a 4th participant after 3 expenses no longer changes past balances.

---

### Prompt 5 — Delete participant validation & edit/delete expenses
**Mode:** Agent
```
Two issues:
1. Removing a participant who paid for or is included in an expense should be blocked with a 
   clear message — not silently corrupt the data.
2. Add Edit and Delete buttons to each expense. On delete, recalculate balances. On edit, 
   allow changing description and amount (not payer or split group), recompute splits for 
   that expense, and re-render settlement.
After edit, confirm the settlement view updates immediately (not cached from old state).
```
**Outcome:** Accepted — added `removeParticipant` guard that checks expense involvement, and `editExpense`/`deleteExpense` functions. Verified: editing hotel from $300 to $200 correctly updates Ana's balance from +130 to +63.33.

---

### Prompt 6 — Input validation hardening & JSON export
**Mode:** Agent
```
Harden input validation:
- Amount field: reject "abc", "0", "-50", "12.345" (more than 2 decimals)
- Empty description: rejected
- Payer not selected: rejected
- Duplicate participant name (case-insensitive): rejected

Also add an "Export JSON" button that downloads the full trip state (participants, expenses, 
balances, settlements) as a formatted JSON file.
```
**Outcome:** Accepted — added regex validation `^\d+(\.\d{1,2})?$` for amounts, case-insensitive duplicate check with `.toLowerCase()`, and a `exportJSON()` function creating a Blob download. Tested all rejection cases manually.
