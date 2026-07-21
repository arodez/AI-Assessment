# Product Brief — Trip Expense Splitter

## What is being built

A single-page web application called **Trip Split** that allows a group of friends to track shared expenses during a trip and calculate who owes whom at the end. The app provides a shared view (no authentication) where participants can log expenses and see real-time settlement calculations.

## Target users

A group of friends on a trip who need a quick, shared way to track who paid for what and settle up fairly afterward. No technical expertise assumed — the UI must be self-explanatory.

## Functional requirements

1. **Add/remove participants** by name (unique, non-empty, trimmed).
2. **Add expenses** with: description (non-empty), amount (positive number, max 2 decimal places), and payer (selected from a dropdown of existing participants — never free text).
3. **Equal split** — every expense is split equally among ALL current participants at the moment the expense is added. The expense stores a snapshot of participants at creation time; adding someone later does NOT retroactively change past splits.
4. **Balances view** — for each person, show total paid minus their fair share. The sum of all balances must always equal zero.
5. **Settlement view** — a minimal list of "X pays Y $Z" transfers that zeroes all balances (fewest transfers preferred).
6. **Persistence** — all data stored in localStorage. Refreshing the page restores the full trip state. A "Reset Trip" button with a confirmation dialog.

## Stack & constraints

- **Stack:** Single HTML file with embedded CSS and vanilla JavaScript. No frameworks, no build step, no backend.
- **How to run:** Open `index.html` in any modern browser.
- **Do NOT include:** currency conversion, receipt scanning, authentication, or any feature not listed above.

## Money-handling rules

- Store all monetary amounts internally as **integer cents** to avoid floating-point errors.
- Display as dollars with exactly 2 decimal places.
- When a split doesn't divide evenly (e.g., $100 / 3 = 33.33 each with 1 cent remainder), distribute the leftover cent(s) to the **first participant(s) in alphabetical order** deterministically so totals always reconcile exactly.

## Edge cases to handle

1. **Amount = 0 or negative** → rejected with a clear error message; balances remain unchanged.
2. **Non-numeric amount** (e.g., "abc") → rejected with error, page does not break.
3. **Rounding** (e.g., $100 split 3 ways) → integer cents with deterministic remainder distribution; balances must sum to exactly zero.
4. **Participant added after expenses exist** → past expenses are NOT recalculated; new participant only included in future expenses.
5. **Delete participant who has paid or owes** → blocked with an explanation message ("settle first" or "remove their expenses first"). Undefined silent behavior is not acceptable.
6. **Expense added with only 1 participant** → allowed (that person pays and owes the full amount, net zero).
7. **Duplicate participant name** → rejected (case-insensitive comparison, trimmed).

## Acceptance criteria

With participants **Ana, Bruno, Carla** and expenses:
- Ana pays $300.00 (hotel)
- Bruno pays $150.00 (dinner)
- Carla pays $60.00 (taxi)

The app must show:
- **Total:** $510.00 → fair share $170.00 each
- **Balances:** Ana +$130.00 · Bruno −$20.00 · Carla −$110.00 (sum = 0)
- **Settlement:** Carla → Ana $110.00, Bruno → Ana $20.00 (2 transfers that zero all balances)
- After a **page refresh**, all data and calculations persist unchanged.

## Bonus features (if time permits)

- Unequal splits (per-expense participant selection)
- Edit/delete expenses with correct balance recalculation
- Export trip data to JSON
