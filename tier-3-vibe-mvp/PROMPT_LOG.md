# Prompt Log
> Record **every** prompt sent to the AI, in order, unedited. Add a one‑line note on what you did with the response (accepted / modified / rejected). Exported chat links or screenshots may be attached instead, but the accept/modify/reject notes are still required.
## Tool & Workflow Note
**Tool used:** Antigravity (ChatGPT‑based coding assistant)  
**Mode(s) used:** chat (interactive)  
**Notable limitations or surprises:** None significant; the tool handled the full end‑to‑end implementation flow without issues.
---
### Prompt 1
**Mode:** chat 
> Using BRIEF.md as a base for project structure, database schema and tech stack. Use updated versions of the dependencies.
Build the event creation form and the public upcoming events list.
* **Outcome:**  accepted – created an implementation plan, then built the Next.js app with SQLite, event‑creation form, and public events list.

### Prompt 2
**Mode:** chat
> Please update the event creation to prevent create events with the same title
* **Outcome:**  accepted – added duplicate‑title validation in the POST /api/events handler and created a unique index on events.title (case‑insensitive).

### Prompt 3
**Mode:** chat
> Create the dashboard for organizers to view attendees and export to CSV.
* **Outcome:**  accepted – implemented an organizer dashboard (src/app/dashboard/page.js), an attendees‑API (src/app/api/events/[eventId]/attendees/route.js) with CSV export, and updated the top‑level README.

### Prompt 4
**Mode:** chat
> Please implement the files and add the changes to the README file
* **Outcome:**  accepted – added the dashboard page, attendees API, and README bullet describing the new dashboard feature.