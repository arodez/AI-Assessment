# Frontend Phase — Community Events Hub

## Context

The database and backend/API phases are both done and committed (`PLAN-database.md`, `PLAN-backend.md`; API documented in `solution/backend/docs/API.md`). This phase builds the React SPA against that already-working API, pixel-matching the 4 mockup screens in `mockups/project/*.dc.html`. Repo is greenfield for frontend — no `package.json`/`solution/frontend/` exists anywhere.

Confirmed with the user before designing:
- **TypeScript** (strict mode, matching the backend's mypy strictness).
- **CSS Modules + a central `tokens.css`** (CSS custom properties) — not Tailwind, not CSS-in-JS.
- **TanStack Query** for server state (queries + mutations with cache invalidation).
- **react-hook-form + zod** for the Create Event form specifically.
- **Vite** + **React Router** (not asked — obvious/standard choices for a from-scratch 4-screen SPA; Vite's default port 5173 already matches the backend's `CORS_ALLOWED_ORIGINS` default, set up during the backend phase).

**Known gotcha, unresolved from earlier phases**: Node 26.6.0 is installed via asdf but not activated anywhere (`node --version` fails with "No version is set"). Must be fixed as the first setup step via a tier-root `.tool-versions` file.

**Also noticed, explicitly out of scope for this phase**: `CLAUDE.md` requires `SECURITY_CHECK.md` and `VERIFICATION_NOTE.md` under `solution/`; neither exists after two completed phases. Flagging it here rather than silently ignoring it — not this phase's job to backfill, but worth deciding when to circle back.

**Two real gotchas this plan is built around, not glossed over**:
1. `GET /events`/`GET /event/:id/details`'s `viewer_status` (`"confirmed"|"cancelled"|null`) and `GET /event/:id/attendance`'s `status` (`"Confirmed"|"Cancelled"`) are **different types** in the API — must not be unified into one TS union.
2. The mockups' own JS is 100% fake: localStorage role-by-email-substring "auth", client-only RSVP state toggling, a 5-column CSV builder with a nonexistent `Team` field. Every mockup behavior below states what's replaced with a real API call versus what visual/interaction pattern is kept as-is.
3. **The "low spots" badge threshold isn't defined anywhere** (not in BRIEF, not in the API, not numerically in the mockup — it only demonstrates the visual state). **Resolved**: `remaining/total < 20%`.

## Status

In progress.
- [ ] Vite scaffold + toolchain (`.tool-versions`, deps, tsconfig)
- [ ] Design tokens + fonts
- [ ] API client layer
- [ ] Auth context + route guards
- [ ] TanStack Query wiring + routing
- [ ] Shared UI primitives
- [ ] Login screen
- [ ] Feed screen
- [ ] Create Event screen
- [ ] Organizer View screen
- [ ] Test suite
- [ ] Docs (frontend README + top-level solution/README.md)
- [ ] Full verification run

## Approach

### 1. Project setup

```bash
cd solution && npm create vite@latest frontend -- --template react-ts
```

**`.tool-versions` fix** — add `tier-3-vibe-mvp/.tool-versions` (repo/tier root, not inside `solution/frontend/`) containing `nodejs 26.6.0`. Placed at the tier root because asdf resolves by searching the current directory and every parent, and it's exactly the path asdf's own error message pointed at. asdf's `.tool-versions` format needs an exact, actually-installed version (26.6.0, confirmed via `asdf list nodejs`) — it doesn't understand semver-range syntax like `^26.0.0`. That range instead goes into `package.json`'s `engines` field: `"engines": { "node": "^26.0.0" }`, declaring "any Node 26.x" as the project's actual requirement for anyone running this outside of asdf, while `.tool-versions` handles activating a concrete version on this machine.

Dependencies added on top of the Vite scaffold — runtime: `react-router-dom`, `@tanstack/react-query`, `react-hook-form`, `zod`, `@hookform/resolvers`. Dev: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`, `prettier` + `eslint-config-prettier` (ESLint/TS already scaffolded by Vite).

`tsconfig.app.json` gains `noUncheckedIndexedAccess`, `noImplicitOverride`, `noFallthroughCasesInSwitch` on top of Vite's already-`strict: true` — the closest TS analogue to the backend's mypy rigor. `exactOptionalPropertyTypes` deliberately **not** enabled — fights react-hook-form's/TanStack Query's own types more than it's worth for an MVP.

`package.json` gains `"engines": { "node": "^26.0.0" }`.

`solution/frontend/.env.example` → `VITE_API_BASE_URL=http://localhost:5000`, read via `import.meta.env.VITE_API_BASE_URL`.

### 2. Design tokens (`src/styles/tokens.css`)

One `:root { --token: value }` file imported once in `main.tsx`, giving every CSS Module the same custom properties. Full token set (colors, category-chip colors keyed by the exact backend enum values, fonts, radii, spacing, shadows) extracted verbatim from the 4 mockup files — see the token table below.

**Fonts** copied from `mockups/project/assets/fonts/` into `solution/frontend/src/assets/fonts/` (not `public/`, so Vite content-hashes them and fails loudly on a bad path instead of silently 404ing). **The 7 mockup photos are explicitly NOT copied** — the backend already serves real seeded event images at `/uploads/events/<file>`; the frontend only ever needs to prefix `image_url` with `VITE_API_BASE_URL`.

```css
:root {
  --color-bg:#FCFBF5; --color-text:#211E1E; --color-brand:#E93D44; --color-border:#E4E3DD;
  --color-link:#1366B1; --color-link-hover:#0f4f88; --color-muted:#a2a19c;
  --color-body-secondary:#5c5a57; --color-label:#797873; --color-error:#BA2229;
  --color-chip-neutral-bg:#F1F0EA; --color-table-header-bg:#F7F6F0;
  --color-registered-bg:rgba(50,168,135,.16); --color-registered-text:#1f6f57;
  --color-confirmed-pill-bg:rgba(50,168,135,.15); --color-low-spots-bg:#FFCFD6;
  --color-avatar-default:#26BDFB; --shadow-card-tint:rgba(33,30,30,.04);
  --shadow-modal-backdrop:rgba(33,30,30,.6); --shadow-modal:rgba(33,30,30,.3);
  --color-modal-close-bg:rgba(255,255,255,.92);

  /* Category chip colors — keys MUST equal backend EventType enum values */
  --color-study-group-bg:#1366B1; --color-study-group-text:#fff;
  --color-ama-bg:#8021F8;         --color-ama-text:#fff;
  --color-workshop-bg:#32A887;    --color-workshop-text:#fff;
  --color-social-bg:#DDFD58;      --color-social-text:#211E1E;
  --color-other-bg:#797873;       --color-other-text:#fff;

  --avatar-colors:#26BDFB,#32A887,#8021F8,#FF5D5E,#1366B1;
  --font-display:'Space Mono',monospace; --font-body:'Nunito Sans',sans-serif;

  --radius-chip:5px; --radius-logo:6px; --radius-control:7px; --radius-thumb:8px;
  --radius-card:10px; --radius-modal:12px; --radius-circle:50%;

  --header-padding:20px clamp(20px,4vw,56px);
  --main-padding:clamp(28px,4vw,52px) clamp(20px,4vw,56px) 80px;
  --card-body-padding:16px 18px 18px; --card-body-padding-compact:12px 14px 14px;
  --card-grid-gap:24px; --section-margin-bottom:40px;

  --shadow-card:0 1px 2px var(--shadow-card-tint);
  --shadow-modal-panel:0 20px 60px var(--shadow-modal);
  --shadow-registered-ring:0 0 0 2px #32A887,0 1px 2px var(--shadow-card-tint);
}
```

Responsiveness follows the mockups exactly: **no media queries anywhere** — `clamp()` for fluid spacing/type, `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))` for card grids, `flex-wrap: wrap`.

### 3. API client layer (`src/api/`)

`types.ts` — typed 1:1 against `docs/API.md`, including the two asymmetric status unions from Context (`ViewerStatus` vs `AttendanceStatus`, never merged).

`client.ts` — `apiFetch<T>(path, init?)`: prefixes `VITE_API_BASE_URL`, attaches `Authorization: Bearer <token>`, parses non-2xx bodies into a typed `ApiError` (`.code`/`.status`/`.details`), handles `204` without attempting to parse a body (needed for `DELETE /event/:id/register`). Token access goes through a standalone `tokenStore.ts` (plain module-level variable, no React import) so the fetch layer has zero React dependency and can't circularly import `AuthContext`. A separate `downloadFile(path)` helper handles the one non-JSON endpoint (CSV export): fetches with the auth header, returns `{ blob, filename }` parsed from `Content-Disposition`.

`events.ts` / `auth.ts` / `registrations.ts` / `attendance.ts` — one thin typed function per endpoint (`login`, `listEvents`, `getEvent`, `createEvent`, `registerForEvent`, `cancelRegistration`, `getAttendance`, `downloadAttendanceCsv`). React Query hooks wrap these in a separate `src/hooks/` layer, keeping `src/api/` framework-agnostic and unit-testable without React Testing Library.

### 4. Auth (`src/auth/`)

`AuthProvider`: `{token, user}` initialized **synchronously** from `localStorage` (`useState(() => readStoredAuth())`, not a `useEffect`) — no logged-in-user-briefly-sees-login-page flash, and `tokenStore` is primed before any query fires on first paint. Single JSON blob under one `localStorage` key (`eventsHubAuth`), not the mockup's fragile two-separate-keys scheme. `login(email)` calls the real API, `logout()` clears everything and the header's "Switch account" link uses it.

`RequireAuth` / `RequireAdmin` route guards redirect appropriately. **Explicit note carried into the code comments**: these are UX convenience only — every admin-only mutation is independently enforced server-side with a real `403`; no security depends on the React guard.

### 5. TanStack Query wiring

Query keys: `eventKeys.list()`, `eventKeys.detail(id)`, `eventKeys.attendance(id)`. Mutations: registering `setQueryData`s the detail with the API's returned updated event (instant UI, no refetch) **and** invalidates the list (so remaining-spots/viewer-status stay correct everywhere); cancelling invalidates both detail and list (DELETE returns no body, nothing to `setQueryData` with); creating an event invalidates the list then navigates to `/events`. Register/cancel deliberately do **not** invalidate `eventKeys.attendance(id)` — that's a different admin screen, no live-polling layer in this MVP, noted as an accepted limitation rather than glossed over.

### 6. Routing

```
/                          -> redirect to /login
/login                     -> LoginPage (redirects to /events if already authed)
/events                    -> RequireAuth -> FeedPage
/events/new                -> RequireAuth -> RequireAdmin -> CreateEventPage
/events/:id/attendance     -> RequireAuth -> RequireAdmin -> OrganizerViewPage
*                          -> redirect to /login
```

`/login` is the effective default/landing route, per explicit direction: an unauthenticated visitor always lands on Login first (root `/` and any unmatched path redirect there), and `/login` itself immediately forwards an already-authenticated visitor on to `/events` — so being logged in still feels like landing on the feed, without `/events` ever being reachable as a default for someone who isn't authenticated.

The Feed's event detail is an in-page modal driven by component state (`selectedEventId`), not a route — matching the mockup's actual interaction model rather than inventing a `/events/:id` route the mockups never show.

### 7. Components

Shared primitives: `Badge` (generic pill), `CategoryChip` (keyed by enum value, not the mockup's Title Case label), `SpotsBadge`, `StatusPill`, `Avatar` (initials + rotating color), `Modal` (backdrop/close/Escape, composed by `EventDetailModal` rather than reimplemented).

`AppHeader` shared across all 3 authenticated pages. Feed: `EventCard` (grid item) + `EventCta` (extracted so `EventDetailModal` shares the exact same Sign-up/Cancel/Full branching, not a copy) + `WeekSection` + `FeedPage`. Create Event (admin): `CoverPhotoUpload`, `CategoryTypeSelector`, `LocationTypeToggle`, `CreateEventForm` (whose live preview pane literally reuses `EventCard`, not a second hand-rolled layout), `CreateEventPage`. Organizer View (admin): `OrganizerHeader`, `AttendeeTable`, `OrganizerViewPage`.

`src/utils/eventStatus.ts` — single source of truth for badge/CTA branching, shared by `SpotsBadge` and `EventCta` so they can't drift apart:

```ts
type EventDisplayState = 'registered' | 'cancelled' | 'full' | 'low' | 'open';

function deriveEventDisplayState(remaining: number, total: number, viewerStatus: ViewerStatus): EventDisplayState {
  if (viewerStatus === 'confirmed') return 'registered';
  if (viewerStatus === 'cancelled') return remaining <= 0 ? 'full' : 'cancelled';
  if (remaining <= 0) return 'full';
  if (remaining / total < 0.2) return 'low';
  return 'open';
}
```

### 8. Create Event form

zod schema mirrors every backend rule (title 3–140 trimmed, positive integer spots, end-after-start, hybrid/virtual requires an `http(s)://` location entry, length caps on description/host fields), wired via `@hookform/resolvers`'s `zodResolver`. Client-side image pre-check (mime type, ≤5MB) for fast feedback only — dimension/re-encode validation stays server-only (Pillow), the API is the authority.

`buildFormData.ts` maps validated form values to the multipart body: `start`/`end` combine `date`+`time` into `${date}T${time}:00` (no timezone suffix — matches the backend's naive-datetime storage, deliberately not `Date.toISOString()`); `location` is built from the room/link fields per location type then `JSON.stringify`'d into a single form field per the API's documented convention; blank optional fields are omitted rather than sent as `""`.

**Cover photo — deliberate simplification**: the mockup's `image-slot.js` supports drag-to-reposition/pinch-zoom crop framing (prototyping tooling with no backing concept in the real API — no crop-offset field exists anywhere). `CoverPhotoUpload` implements drag-and-drop + click-to-browse + an object-URL preview + "Remove" — no pan/zoom/crop UI.

### 9. Testing (Vitest + React Testing Library)

`vite.config.ts` test block (`jsdom`, `setupTests.ts`). API mocking via `vi.mock()` on `src/api/*.ts` directly (no MSW — simpler at this scale). Coverage aims for the same rigor as the backend's 73 tests, not smoke tests:

- `api/client.test.ts` — error-envelope parsing, auth header attachment, 204-no-body handling
- `utils/eventStatus.test.ts` — every branch (full/low-by-percent/open/registered/cancelled-still-open/cancelled-now-full)
- `utils/weekGrouping.test.ts` — week-bucket boundary conditions
- `CategoryChip.test.tsx` — all 5 `event_type` values including `other`
- `EventCard.test.tsx` — full CTA branching, card-click-vs-CTA-click event propagation
- `LoginPage.test.tsx` — validation, checking-state, real 401 handling, redirect on success
- `RequireAuth.test.tsx` / `RequireAdmin.test.tsx` — all three redirect/pass-through cases
- `CreateEventForm.test.tsx` — every validation error, and a valid submit producing correctly-shaped `FormData`
- `CoverPhotoUpload.test.tsx` — drag-drop, remove, non-image rejection
- `AttendeeTable.test.tsx` — cancelled-row styling
- `OrganizerViewPage.test.tsx` — clipboard copy is exactly 4 columns (not the mockup's 5), CSV export hits the real endpoint rather than rebuilding client-side

### 10. Docs

`solution/frontend/README.md` — setup/run/build/test/lint/typecheck commands, project layout, and an explicit "known simplifications vs. mockups" section (no crop UI, CSV via real endpoint, guards are UX-only).

**`solution/README.md` (new — the still-missing top-level doc)**: ties both phases together — prerequisites, backend startup (`poetry install && flask db-setup && flask run`, port 5000), frontend startup (`npm install && npm run dev`, port 5173), the seeded login emails table (copied from the backend README), links out to `BRIEF.md`/backend docs/frontend README, and a ports note.

## Verification

Automated: `npm run build`, `npx tsc --noEmit`, `npm run lint`, `npm test` — all clean.

Manual, both servers running, using seeded accounts (`alice.kim@company.com` admin, `diego.ramirez@company.com` attendee):
1. Login as attendee → `/events`, week sections computed correctly.
2. Register for an open event → card flips to "You're going ✓" without a full reload; remaining spots decrements.
3. Cancel → "Sign up again"; re-register → back to confirmed — proves the backend's update-not-duplicate behavior surfaces correctly.
4. Attempt the seeded full event (id 4) → CTA disabled/"Fully booked".
5. "Switch account" clears storage, redirects to `/login`; a hard refresh on `/events` afterward also redirects (no stale token).
6. Login as admin → "+ Create an Event" visible; attendee doesn't see it, and manually navigating to `/events/new` as attendee redirects away.
7. Create an event with an uploaded photo and a valid hybrid location URL → appears correctly on the feed, image loads via the backend's `/uploads/...` route.
8. From that event's modal (as admin) → "Attendance List" → Organizer View loads with correct (empty) roster/stats.
9. On a seeded event with real registrations: "Copy to clipboard" produces exactly the 4-column shape; "Export CSV" downloads a file with header exactly `full_name,email,sign_up_at,status`.
10. Direct URL navigation to admin-only routes while logged out redirects to `/login`; visiting `/` (or any unmatched path) while logged out also lands on `/login`, not `/events`. Visiting `/` or `/login` directly while already authenticated forwards straight through to `/events`.
11. No CORS errors in devtools throughout.
12. Visual pixel-match pass: screenshot all 4 running screens and compare against `mockups/screenshots/*.png`.
