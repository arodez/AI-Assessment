# Community Events Hub — Frontend

React 19 + TypeScript + Vite single-page app for the Community Events
Hub MVP: login, event feed, RSVP, event creation, and the organizer
attendance view. Talks to the Flask API in
[`../backend`](../backend) — see [`../BRIEF.md`](../BRIEF.md) for the
overall product spec and [`../backend/docs/API.md`](../backend/docs/API.md)
for the endpoint reference this app is built against.

## Prerequisites

- Node.js ^26.0.0 (an asdf `.tool-versions` pinning `nodejs 26.6.0` lives
  in this directory — `asdf install` picks it up automatically once you
  `cd` here if you use asdf; otherwise install a matching Node yourself)
- The backend running locally (see [`../backend/README.md`](../backend/README.md))
  — this app has no mock-data mode, every screen talks to the real API

## Setup

```bash
npm install
cp .env.example .env   # defaults are fine as-is; only edit if the backend
                        # runs somewhere other than http://localhost:5000
```

## Running

```bash
npm run dev
```

Opens on `http://localhost:5173` (matches the backend's default
`CORS_ALLOWED_ORIGINS`). You'll land on `/login` — log in with one of the
backend's seeded emails (see the table in
[`../backend/README.md`](../backend/README.md#seeded-accounts); admin
accounts can create events and view the organizer attendance screen,
attendee accounts can browse and RSVP).

## Scripts

```bash
npm run dev             # start the dev server
npm run build           # production build (tsc -b && vite build)
npm run typecheck       # tsc -b --noEmit
npm run lint             # oxlint
npm run format           # prettier --write
npm run format:check     # prettier --check
npm test                 # vitest run
npm run test:watch       # vitest (watch mode)
npm run test:coverage    # vitest run --coverage
```

## Project layout

```
src/
  api/            Typed fetch wrappers, one file per resource — framework-
                   agnostic (no React import), unit-testable on their own
  auth/           AuthContext/AuthProvider (localStorage-backed), route guards
  hooks/          TanStack Query hooks (queries + mutations) wrapping api/
  schemas/        zod schema(s) for form validation (Create Event)
  components/     Shared UI + per-screen composed components
  pages/          LoginPage, FeedPage, CreateEventPage, OrganizerViewPage
  styles/         tokens.css — the one design-tokens file every CSS Module reads
  utils/          Pure helpers (date formatting, week grouping, CSV building, ...)
  test/           Shared test fixtures/helpers (not app code)
```

Styling is CSS Modules throughout, keyed off `styles/tokens.css`'s custom
properties — no Tailwind, no CSS-in-JS. Server state goes through
TanStack Query; the only local component state is UI-only (form inputs,
modal open/closed, transient "Copied!" flags).

## Known simplifications vs. the mockups

The mockups (`../../mockups/project/*.dc.html`) are fully-interactive
prototypes, but their JS is 100% fake — localStorage role-by-email-
substring "auth", client-only RSVP toggling with no server, and CSV data
that includes fields with no backing API field. This build replaces all
of that with the real API and drops what has no real equivalent:

- **Cover photo upload** — the mockup's `image-slot.js` supports drag-to-
  reposition/pinch-zoom crop framing. There's no crop-offset field
  anywhere in the real API, so `CoverPhotoUpload` only does drag-and-drop
  / click-to-browse / preview / remove — no pan or zoom UI.
- **Organizer attendance export** — the mockup's CSV has 5 columns
  including a `Team` field it invents from randomly-generated fixture
  data. The real roster only ever has 4 columns
  (`full_name,email,sign_up_at,status`, per `GET /event/:id/attendance`),
  so that's what both "Copy to clipboard" and "Export CSV" produce.
  "Export CSV" downloads the backend's own file rather than rebuilding it
  client-side; "Copy to clipboard" builds the same 4-column shape from
  the already-fetched roster since there's no copy endpoint.
- **Route guards are UX only.** `RequireAuth`/`RequireAdmin` just avoid
  flashing a page that would immediately fail every request it makes —
  every admin-only mutation is independently enforced server-side with a
  real `403`. No security depends on the React guards.
- **`viewer_status` vs. attendance `status` are deliberately separate
  types**, not unified — see the doc comment at the top of
  `src/api/types.ts` for why.
- **"Low spots" threshold** (remaining/total < 20%) isn't specified in
  BRIEF, the API, or the mockup (which only demonstrates the visual
  state) — confirmed with the product owner rather than assumed; see
  `src/utils/eventStatus.ts`.

## Testing

Vitest + React Testing Library. API modules are mocked with `vi.mock()`
directly (no MSW) — simple enough at this scale. Coverage is currently
~87% statements; see `npm run test:coverage` for the full breakdown.
