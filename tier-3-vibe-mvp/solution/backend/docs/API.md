# API Reference

Full HTTP API reference for the Community Events Hub backend. Source of
truth for scope/behavior is [`../../BRIEF.md`](../../BRIEF.md) §7.1/§7.4 —
this document explains how that contract is actually implemented, plus the
things it doesn't cover that this phase had to fill in.

## Auth

`POST /login` takes only a company email — no password, no MFA. Because
account creation is out of scope for this MVP, login **never creates a
User row**; it only succeeds for an email matching one of the seeded
fixture users (case-insensitive), listed in
[`../README.md`](../README.md#seeded-accounts).

```bash
curl -s -X POST localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"email": "alice.kim@company.com"}'
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": { "id": 1, "first_name": "Alice", "is_admin": true }
}
```

Send the token as `Authorization: Bearer <token>` on every subsequent
request. It carries `sub` (user id), `email`, `is_admin`, expires after
`JWT_ACCESS_TOKEN_EXPIRES_HOURS` (24h by default), and there is no
refresh/logout flow — the frontend just discards it client-side on
"Switch account."

## Endpoints

All request/response bodies are JSON **except** `POST /event`, which is
`multipart/form-data` (see below).

| Method & path | Auth | Notes |
|---|---|---|
| `POST /login` | none | See above |
| `GET /events` | any user | Future events only, sorted by `start` ascending |
| `GET /event/:id/details` | any user | Single event, no attendee data |
| `POST /event` | admin | multipart/form-data, see below |
| `GET /event/:id/attendance` | admin | Full roster |
| `GET /event/:id/attendance/download` | admin | CSV roster |
| `POST /event/:id/register` | any user | Caller registers themself |
| `DELETE /event/:id/register` | any user | Caller cancels their own registration |

Event ids in the path are validated as `400` (not `404`) if the segment
isn't a positive integer — see [`app/routes/helpers.py`](../app/routes/helpers.py).

### `GET /events` / `GET /event/:id/details` — response shape

```json
{
  "id": 1,
  "title": "Engineering AMA: Platform Roadmap Q3",
  "start": "2026-08-14T12:00:00",
  "end": "2026-08-14T13:00:00",
  "spots": 40,
  "remaining_spots": 38,
  "event_type": "ama",
  "location_type": "hybrid",
  "description": "...",
  "image_url": "/uploads/events/ama-room.jpg",
  "location": ["Auditorium A, HQ Floor 3", "https://zoom.us/j/1112223333"],
  "host_name": "Alice Kim",
  "host_team": "Platform Engineering",
  "viewer_status": null,
  "created_at": "2026-08-07T18:19:15.701242",
  "updated_at": "2026-08-07T18:19:15.701242"
}
```

`GET /events` returns an array of these; `GET /event/:id/details` returns
one. Two fields go beyond BRIEF's literal schema — see "Gaps filled in
this phase" below for why: `remaining_spots` and `viewer_status`
(`"confirmed" | "cancelled" | null` — whether the **calling** user is
registered for this event).

### `POST /event` — multipart/form-data

Form fields (all arrive as strings; validated by
[`EventCreateRequest`](../app/schemas/event.py)):

| Field | Required | Rule |
|---|---|---|
| `title` | yes | 3–140 chars after trim |
| `start`, `end` | yes | ISO-8601 datetime; `end` strictly after `start` |
| `spots` | yes | positive integer |
| `event_type` | yes | `study_group` \| `ama` \| `workshop` \| `social` \| `other` |
| `location_type` | yes | `in_person` \| `hybrid` \| `virtual` |
| `description` | no | ≤2000 chars |
| `location` | no | **JSON-encoded string** — see below |
| `host_name`, `host_team` | no | ≤100 chars each |
| `image` | no | file part — see Cover photo rules below |

`multipart/form-data` has no native array type, so `location` (BRIEF's
`array(text)`) is sent as a single field containing a JSON-encoded array:

```js
formData.append("location", JSON.stringify(["Room 12", "https://zoom.us/j/123"]));
```

If `location_type` is `virtual` or `hybrid`, at least one `location`
entry must be a well-formed URL (`http(s)://...`) — a plain room name
alone is rejected.

```bash
curl -s -X POST localhost:5000/event \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F title="Docker Basics" \
  -F start="2026-09-15T10:00:00" \
  -F end="2026-09-15T11:00:00" \
  -F spots=10 \
  -F event_type=workshop \
  -F location_type=in_person \
  -F image=@cover.jpg
```

#### Cover photo validation

The uploaded `image` file must be jpeg/png/webp, verified from its actual
content (Pillow's own format detection) — not the filename extension or
the client's `Content-Type` header. This also rejects SVG (can carry
embedded scripts) and any renamed non-image file. Bounds: minimum
400×250px, maximum 4000×4000px and 5MB. Accepted files are re-encoded
(dropping EXIF/ICC metadata) and saved under a server-generated filename
— never the client's — then served back at `/uploads/events/<file>`.

### `GET /event/:id/attendance` — response shape

```json
[
  {
    "full_name": "Grace Hopper",
    "email": "grace.hopper@company.com",
    "sign_up_at": "2026-08-08T09:00:00",
    "status": "Confirmed"
  }
]
```

Includes both `Confirmed` and `Cancelled` rows — a cancellation is a
status flip, not a deletion, so organizers can see the full history.

### `GET /event/:id/attendance/download`

CSV with the same four columns (`full_name,email,sign_up_at,status`),
`Content-Type: text/csv`, filename
`<slugified-title>-<start:YYYY-MM-DD>-<today:YYYY-MM-DD>.csv`.

### `POST /event/:id/register` / `DELETE /event/:id/register`

Both act on the **caller's own** registration (identity from the JWT, not
the request body). `POST` returns the updated event (same shape as
`GET /event/:id/details`) with `201`; `DELETE` returns `204` with no
body. See [`app/routes/registrations.py`](../app/routes/registrations.py)
for the full/duplicate/re-signup-after-cancel branching logic.

## Error envelope

Every non-2xx response has this shape:

```json
{ "error": "event_full", "message": "This event is full.", "details": null }
```

`error` is a stable, machine-readable code — `message` is for humans,
`details` is populated (a list of `{field, message}`) only for
`validation_error`. Codes used across the API:

| `error` | Status | When |
|---|---|---|
| `validation_error` | 400 | A request field failed a rule in the tables above |
| `bad_request` | 400 | Malformed event id in the URL |
| `event_full` | 400 | No remaining spots |
| `already_registered` | 400 | Caller already has a `Confirmed` registration |
| `no_active_registration` | 400 | Nothing to cancel (never registered, or already cancelled) |
| `missing_token` / `invalid_token` / `token_expired` | 401 | No/garbled/expired `Authorization` header |
| `unauthorized` | 401 | Login with an unrecognized email |
| `forbidden` | 403 | Non-admin hitting an admin-only route |
| `not_found` | 404 | Event id doesn't exist |
| `method_not_allowed` | 405 | Wrong HTTP method for the route |
| `payload_too_large` | 413 | Request body over `MAX_CONTENT_LENGTH_MB` |
| `internal_error` | 500 | Unexpected server error |

`403` is reserved purely for admin/authorization failures — every
business-rule rejection (full event, duplicate signup, nothing to cancel)
is a `400` with its own code, so the frontend can distinguish "you did
something wrong" from "you're not allowed to do that at all."

## Gaps filled in this phase

BRIEF's endpoint table (§7.4) doesn't cover three things the app can't
actually work without — each a deliberate, documented addition rather
than silent scope creep:

1. **No route to serve uploaded images.** Fixed by repurposing Flask's
   built-in static handling (`static_folder`/`static_url_path="/uploads"`
   in [`app/__init__.py`](../app/__init__.py)) rather than a hand-written
   route — `Event.image` paths become loadable at `/uploads/events/<file>`
   for free, with Flask's already-hardened static handler (conditional
   GET/ETag, path-traversal protection).
2. **`viewer_status` on every event.** The mockups' Feed screen renders a
   different CTA per event ("Sign up" / "You're going ✓" / "Cancel")
   based on whether the *calling* user is registered — there's no other
   way for the frontend to know that without an extra round-trip per
   card, so `GET /events` and `GET /event/:id/details` both include it.
3. **A `user` object alongside the login token.** The mockups greet by
   first name ("Hey, Jordan") and gate UI on `is_admin` — the JWT itself
   only carries `email`/`is_admin`, not `first_name`, so `POST /login`
   returns a small `user` object too.

## Try it

- **curl**: examples throughout this doc, or the full walkthrough in
  [`../README.md`](../README.md#running-the-api).
- **Postman**: import [`../postman/community-events-hub.postman_collection.json`](../postman/community-events-hub.postman_collection.json)
  and [`../postman/local.postman_environment.json`](../postman/local.postman_environment.json)
  — see [`../postman/README.md`](../postman/README.md).
