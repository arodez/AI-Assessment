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

## Tool & Workflow Note
**Tool used:** Claude (Anthropic) — chat interface with project file context
**Mode(s) used:** chat (interactive)
**Notable limitations or surprises:**
- Project files were provided as a **read-only snapshot** (`/mnt/project`), so fixes could be diagnosed and drafted but not written back directly to the real repo — required manual copy-paste of the corrected file into the actual codebase.
- Diagnosis relied on cross-referencing `AGENTS.md`'s Next.js 15+/16 breaking-change warning rather than live access to `node_modules/next/dist/docs`, since the node_modules folder wasn't part of the shared snapshot.
- No other significant issues; root cause (`params` not awaited in the dynamic attendees route) was identified and fixed in a single pass.

### Prompt 5
**Mode:** chat
> Validate why the project db is not working correctly,there is missing data when I try to retrieve the RSVP attendees
* **Outcome:** accepted – diagnosed the bug: the attendees route (`/api/events/[eventId]/attendees/route.js`) destructured `params` without awaiting it. Since Next.js 15+/16 made dynamic route `params` a Promise, `eventId` resolved to `undefined`, causing the event lookup query to always miss and return "Event not found" / empty attendee data.

### Prompt 6
**Mode:** chat
> Could you write down how the files should be coded to fix this bug
* **Outcome:** accepted – provided the corrected `attendees/route.js` with `const { eventId } = await params;`, plus recommended adding a defensive check for a missing/invalid `eventId` and a reminder to `await params`/`searchParams` in any future dynamic routes per the Next.js 16 breaking-change notes in `AGENTS.md`.