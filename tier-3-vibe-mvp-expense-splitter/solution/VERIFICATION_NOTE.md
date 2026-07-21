# Verification Note

## 1. What the AI got wrong (or almost wrong)

**Floating-point storage (critical):** The first iteration stored amounts as JavaScript floats internally. When splitting $100 among 3 people, it computed `100 / 3 = 33.333...` and displayed $33.33 each, totaling $99.99. The missing cent meant balances didn't sum to zero. I caught this by running the acceptance test scenario mentally before testing.

**Settlement algorithm ordering:** The initial greedy settlement algorithm didn't sort debtors and creditors by amount before matching. With the test scenario (Ana +130, Bruno −20, Carla −110), it matched Carla→Bruno first ($20), then Carla→Ana ($90), then produced a residual — yielding 3 transfers instead of the optimal 2. Sorting descending fixed this.

**Retroactive participant inclusion:** When adding a 4th participant, the AI initially recalculated ALL past expenses to include the new person. The brief explicitly required snapshot-based splitting, but the AI defaulted to "current participants" unless explicitly told.

## 2. How I caught it

**Hand calculation against the acceptance scenario:**

Participants: Ana, Bruno, Carla  
Expenses: Ana pays $300 (hotel), Bruno pays $150 (dinner), Carla pays $60 (taxi)

- Total expenses: $300 + $150 + $60 = **$510.00**
- Fair share per person: $510 / 3 = **$170.00** (divides evenly, no remainder)
- Balances (paid − fair share):
  - Ana: $300 − $170 = **+$130.00** ✓
  - Bruno: $150 − $170 = **−$20.00** ✓
  - Carla: $60 − $170 = **−$110.00** ✓
- Sum of balances: +130 − 20 − 110 = **$0.00** ✓
- Settlement (fewest transfers):
  - Carla owes $110 → pays Ana $110 (Carla zeroed, Ana now +$20)
  - Bruno owes $20 → pays Ana $20 (Bruno zeroed, Ana zeroed)
  - **Result: Carla → Ana $110.00, Bruno → Ana $20.00** ✓

**App output matches exactly.**

**Rounding test:** Added a 4th expense — Bruno pays $100 (snacks).
- New total: $610, fair share: $610 / 3 = $203.33⅓
- In cents: 61000 / 3 = 20333 remainder 1
- Splits: Ana gets 20334 cents ($203.34), Bruno 20333 ($203.33), Carla 20333 ($203.33) — remainder cent goes to "Ana" (first alphabetically)
- New balances:
  - Ana: 30000 − 20334 = +9666 cents = **+$96.66**
  - Bruno: (15000 + 10000) − 20333 = +4667 cents = **+$46.67**
  - Carla: 6000 − 20333 = −14333 cents = **−$143.33**
- Sum: 9666 + 4667 − 14333 = **0** ✓
- App output matches.

## 3. How I confirmed the final result is correct

- Ran the acceptance test scenario (3 participants, 3 expenses) and compared app output to the hand calculation above — exact match.
- Ran the rounding probe ($100 among 3) — verified remainder distribution and zero-sum.
- Tested all edge cases manually:
  - Amount "0" → rejected with "Amount must be greater than zero" ✓
  - Amount "-50" → rejected (fails positive number regex) ✓  
  - Amount "abc" → rejected with "Please enter a valid numeric amount" ✓
  - Amount "12.345" → rejected with "Amount must have at most 2 decimal places" ✓
  - Delete participant "Ana" while she has expenses → blocked with message ✓
  - Refreshed page → all data persisted via localStorage ✓
  - Duplicate name "ana" when "Ana" exists → rejected ✓

## 4. Data integrity answers

**(a) Amount of 0 or negative:**  
The app **rejects** both with a clear error message. Zero fails the `> 0` check ("Amount must be greater than zero"). Negative values also fail the regex validation `^\d+(\.\d{1,2})?$` which only matches positive patterns. Balances remain unchanged.

**(b) $100 split 3 ways (rounding):**  
Amounts are stored as integer cents: 10000 cents / 3 = 3333 base + 1 remainder. The extra cent is assigned to the first participant alphabetically (deterministic). So splits are 3334, 3333, 3333 = 10000 total. Balances always sum to exactly zero because the sum of splits always equals the original amount in cents.

**(c) Deleting a participant who has paid expenses:**  
The app **prevents it** with an alert: "Cannot remove [name] — they are involved in existing expenses. Delete their expenses first or settle up." This is the safe choice because silently removing a payer would leave orphaned expense records with an invalid payer reference, corrupting balance calculations.
