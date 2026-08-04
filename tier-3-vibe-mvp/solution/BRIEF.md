Act as a Senior Frontend Engineer. Create a self-contained, premium Community Events Hub web application using index.html, styles.css, and app.js. 

The application must allow users to:
1. Create events (Title, Date, Description, Max Capacity) with input validation (no past dates, positive capacity, no empty titles).
2. RSVP for events with a valid email. Block duplicate emails for the same event and prevent RSVPs once capacity is reached.
3. View a public list of upcoming events sorted by date, displaying details and remaining capacity.
4. View an organizer dashboard that lists attendees per event and has a button to copy the attendee list to clipboard as CSV format.

Technical Constraints:
- Use Next.Js as sourcecode, SQLLite as database to persist the data
- Write custom CSS (no Tailwind) using CSS variables for a Slate/Indigo theme, glassmorphism card designs, Outfit/Inter typography, and subtle micro-animations for interactivity.
- Ensure all inputs are sanitized to prevent XSS.
- Zero Hardcoded Secrets. Never include raw API keys, passwords, tokens, or private credentials directly in the source code or configuration files.

Acceptance Criteria:
Test and document at least these 3 flows:
- Successful sign-up.
- Rejection when full.
- Rejection of a duplicate email.