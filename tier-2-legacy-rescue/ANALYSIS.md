# Analysis of `report_generator.py`

This script parses a CSV file containing training compliance data for engineers and compiles a text-based compliance report.

## High-Level Functionality
1. **Inputs:** A CSV file (`sys.argv[1]`) with columns `name`, `email`, `team`, `course_status`, and `deadline`.
2. **Outputs:** A structured text file (`sys.argv[2]`) listing counts per course status, total skipped rows, and a list of overdue engineers' emails.
3. **Reference Date:** Checks for overdue engineers against a reference date (defaults to `2026-07-14`).

## Script Structure
* `append_row(row, rows=[])`: Appends a row to a list of rows and returns the list.
* `load_engineers(path)`: Reads the CSV file, skips the header, and builds a list of dictionaries representing valid engineers. It uses a try-except block to skip invalid/short rows and counts skipped rows.
* `count_by_status(engineers)`: Aggregates counts of engineers in statuses: `completed`, `pending`, and `in_progress`.
* `overdue(engineers, today='2026-07-14')`: Identifies engineers who are not `completed` and whose `deadline` is before the reference date.
* `main()`: Orchestrates the pipeline, reading the input CSV, calling the analytic functions, and writing the final report.
