# Trip Split — Expense Splitter

A single-page web app that helps friends split expenses during a trip and shows who owes whom.

## How to Run

1. Open `index.html` in any modern web browser (Chrome, Firefox, Safari, Edge).
2. That's it — no installation, no build step, no server required.

```bash
# Option 1: Double-click index.html in your file manager
# Option 2: From terminal
open index.html        # macOS
xdg-open index.html   # Linux
start index.html      # Windows
```

## Features

- **Add participants** — enter names, enforces uniqueness
- **Add expenses** — description, amount, and who paid (dropdown selection)
- **Equal split** — expenses split equally among all current participants at time of creation
- **Balances** — shows each person's net position (positive = owed money, negative = owes)
- **Settlement** — minimal transfers to zero all balances ("X → Y: $Z")
- **Persistence** — localStorage keeps data across page refreshes
- **Edit/Delete expenses** — with automatic balance recalculation
- **Export JSON** — download full trip data as a file
- **Reset Trip** — clear all data (with confirmation)

## Technical Notes

- All amounts stored internally as integer cents to avoid floating-point drift
- Remainder cents from uneven splits distributed alphabetically (deterministic)
- Participant deletion blocked if they're involved in any expense
- Input validation rejects: empty fields, non-numeric amounts, zero/negative amounts, >2 decimals

## Deliverables

| File | Purpose |
|------|---------|
| `BRIEF.md` | Initial product brief / prompt |
| `PROMPT_LOG.md` | All AI prompts with iteration notes |
| `VERIFICATION_NOTE.md` | Hand-verified math + data integrity answers |
| `index.html` | The complete application |
| `README.md` | This file — startup instructions |
