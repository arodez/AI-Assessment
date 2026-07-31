# Analysis: report_generator.py

**Summary:** Processes engineer training CSV data to generate a weekly compliance status and overdue report.

### Inputs & Outputs
- **Input:** CSV file path (`sys.argv[1]`) containing: `name`, `email`, `team`, `status`, `deadline`.
- **Output:** Text report file path (`sys.argv[2]`) listing status counts, skipped rows, and overdue emails.

### Code Structure
- `append_row(row, rows=[])`: Appends a row to a list (uses problematic mutable default argument).
- `load_engineers(path)`: Reads input CSV, parses columns, and handles malformed rows.
- `count_by_status(engineers)`: Aggregates counts of 'completed', 'pending', and 'in_progress'.
- `overdue(engineers, today)`: Identifies non-completed engineers with deadlines prior to `today`.
- `main()`: Orchestrates execution using command-line arguments.

### Senior Engineer Observations
- **Bugs:** Dead code `SKIPPED += 1` after `continue` in `load_engineers`; global `SKIPPED` is never modified.
- **Bugs:** Mutable default argument `rows=[]` persists state across calls.
