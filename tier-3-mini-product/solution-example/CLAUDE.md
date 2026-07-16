# Developer Conventions — Training Compliance Dashboard

This document defines the development standards, technology stack, and validation rules for the Training Compliance Dashboard.

## 1. Tech Stack
- **Language:** Python 3.10+
- **Backend Framework:** FastAPI with Uvicorn (async handlers)
- **Database:** SQLite (direct sqlite3 for lightweight single-file persistence)
- **Frontend:** Single Page Application (SPA) using Semantic HTML, Vanilla JS (Fetch API), and Vanilla CSS (premium dark-mode design, system fonts, CSS variables, subtle hover micro-animations)
- **Testing:** `pytest` (standard unit and integration tests)

## 2. Ingestion & Validation Rules
- **Schema:** Expects CSV with headers `name,email,team,course,course_status,deadline`.
- **Validation Constraints:**
  - `name`: Must be non-empty string.
  - `email`: Must be non-empty and contain `@`.
  - `team` and `course`: Must be non-empty.
  - `course_status`: Case-insensitive. Normalize to lowercase (`completed`, `pending`, `in_progress`). `Pending` -> `pending`.
  - `deadline`: Must be valid YYYY-MM-DD date.
- **Error Handling:**
  - If a row is missing columns, has blank values for required fields, or contains invalid dates, it must be **rejected and reported** to the user.
  - The ingestion endpoint must never silently drop data or crash the app on bad rows.
  - The API response must return a list of parsed valid rows and a list of rejected rows with details (line number, row content, error reason).

## 3. Overdue Calculation
- **Definition:** An engineer is overdue if:
  - `course_status` is not `completed` (i.e. `pending` or `in_progress`).
  - AND `deadline < system date at runtime` (strict inequality).
- **Boundary Condition:** If `deadline == system date`, the engineer is **not** overdue.
- **Runtime Requirement:** Compare using the live system date (`datetime.date.today()`). No hardcoded dates or client-passed dates for calculation.

## 4. Security & Robustness
- **Secrets Management:** The application must load API keys (e.g., for reminder AI generation) from environment variables or a `.env` file via `python-dotenv`.
- **Git Hygiene:** Add `.env` to `.gitignore`. Never commit API keys, tokens, or credentials to git history.
- **Input Sanitization:** Uploaded files must be validated as text/csv. File size is capped at 5MB.

## 5. Testing Strategy
- Core ingestion parsing, validation, and overdue logic must have unit tests in `test_compliance.py`.
- Tests must cover:
  - Happy path import.
  - Validation failures (missing columns, bad date format, missing email).
  - Overdue date comparisons (past date, future date, today as boundary condition).
