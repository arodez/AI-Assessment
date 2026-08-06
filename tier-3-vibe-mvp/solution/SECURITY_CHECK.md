# Security Check Report

## 1. Secrets & API Keys Check
- **Checked:** Scanned all code files, configuration files, and environment templates.
- **Result:** No production keys or sensitive third-party tokens found. 

## 2. Input Validation Check
- **Checked:** Tested edge cases including empty titles, negative/zero capacities, and malformed emails (`test@domain`).
- **Result:** Initial implementation relied only on frontend validation and allowed invalid direct API payloads.
- **Remediation:** Added server-side validation rules rejecting negative capacities, empty strings, and invalid email string patterns with explicit `400 Bad Request` responses.

## 3. Data Exposure Check
- **Checked:** Inspected public-facing API endpoints and UI components to verify what attendee information is visible.
- **Result:** The public event list originally exposed an array containing all attendee emails.