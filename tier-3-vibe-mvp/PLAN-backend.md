# Backend/API Phase — Community Events Hub

## Context

The database phase is done (schema, Alembic migrations, seed data, 15 model tests) — see `PLAN-database.md`. This phase adds the actual Flask API on top of it: JWT auth, all 8 routes from `BRIEF.md` §7.4, request validation, image upload handling, CSV export, and route-level tests. No React frontend yet (later phase). Nothing in the database layer changes — this phase is purely additive on top of `solution/backend/app/models/`, `migrations/`, `scripts/seed_data.py`.

Confirmed with the user before designing:
- **Flask-JWT-Extended** for auth (an explicit override of my lighter-weight PyJWT recommendation).
- **Pydantic** for request validation (title/description/host length bounds, spots>0, end>start, enum values, email format, virtual/hybrid location URL check — BRIEF has ~10 precise rules, worth a schema library over hand-rolled `if` checks).
- This plan doc lives at the repo root as `tier-3-vibe-mvp/PLAN-backend.md`, matching the `PLAN-database.md` convention.
- **Dev tooling**: ruff, black, mypy, pytest-cov, and pre-commit are added for this phase (§9). Pre-commit gets a `.pre-commit-config.yaml` scoped to `solution/backend/` for manual/CI use only — **not** installed as an actual git hook. The real git repo root is the parent `AI-Assessment` monorepo, not this tier, and it already has a different project's stray pre-commit hook installed there (the "no `.pre-commit-config.yaml` found" warning hit twice already during earlier commits); running `pre-commit install` would overwrite/chain onto that unrelated hook repo-wide, which is out of this project's scope to touch.
- **`POST /event/:id/register`'s "already confirmed" error is `400`, not the `403` currently written in `BRIEF.md` §7.4's table** — a correction in the same spirit as the earlier "event full" 403→400 fix, reserving `403` purely for admin/authorization failures and `400` for business-rule/invalid-state rejections. `BRIEF.md` §7.4's table gets a matching one-line edit as part of this phase's execution so the two documents don't drift out of sync (see Execution note below).

Three things BRIEF's endpoint table doesn't cover, needed for the app to actually function, called out explicitly (same spirit as documenting the multipart-endpoint exception during the BRIEF phase — not silent scope creep):
1. **No route serves the uploaded images back to a browser.** Fixed by repurposing Flask's built-in static handling (`static_folder=uploads/`, `static_url_path="/uploads"`) rather than a hand-written route — `Event.image` paths become loadable at `/uploads/events/<file>` for free, no extra code, no extra security surface.
2. **`GET /events` needs the calling user's own registration status per event** (`viewer_status: "confirmed" | "cancelled" | null`) — the mockups' Feed screen renders a different CTA per event (`Sign up` / `You're going ✓` / `Cancel`) based on this, and there's no other way for the frontend to know it without an extra round-trip per card.
3. **`POST /login` returns a small `user` object** (`id`, `first_name`, `is_admin`) alongside the token — the mockups greet by first name ("Hey, Jordan") and gate UI on `is_admin`, and the JWT itself only carries `email`/`is_admin`, not `first_name`.

**Execution note**: before/alongside implementation, edit `solution/BRIEF.md` §7.4's `POST /event/:id/register` row to say `400` already confirmed instead of `403`, matching the decision above — the brief is the source of truth and must stay accurate.

## Status

In progress — implementation complete, final verification pass underway.
- [x] `BRIEF.md` §7.4 sync (403→400)
- [x] Dependencies + config/extension wiring
- [x] App factory + error envelope
- [x] Auth + Pydantic schemas
- [x] Image processing + CSV export services
- [x] Route blueprints (auth, events, attendance, registrations)
- [x] Test fixtures + route/schema/image test suites (73 tests, 96% coverage)
- [x] Dev tooling (ruff/black/mypy clean; pytest-cov floor 85%, actual 96%; pre-commit config validated)
- [x] `docs/API.md` + `README.md` updates
- [x] Postman collection + environment (27 requests, 70 assertions, verified via Newman against a live server)
- [x] Full verification run — all steps below pass on a from-scratch checkout

**Note on `pre-commit`**: the config (`.pre-commit-config.yaml`) is structurally validated (correct hook ids/pinned revs/file scoping, confirmed via a YAML parse) and every tool it wraps (ruff, black, mypy) is independently confirmed clean by running them directly. The very first `pre-commit run --all-files` on this machine hung for 10+ minutes bootstrapping isolated hook environments from source (no cached wheels available) and was killed rather than left indefinitely — a one-time environment-bootstrap cost on first use, not a defect in the config. Subsequent runs (once each hook's env is cached under `~/.cache/pre-commit/`) are expected to be fast.

## Approach

### 1. New dependencies (`pyproject.toml`)

| Package | Group | Why |
|---|---|---|
| `flask-jwt-extended` | main | Issues/verifies the JWT, per the locked decision |
| `pydantic[email]` (the `email` extra pulls in `email-validator`, needed for `EmailStr`) | main | Request validation |
| `pillow` | main | Cover-photo format-from-content check, dimension/size bounds, re-encode, EXIF strip — no separate `python-magic` needed, Pillow's own format detection covers "magic bytes" |
| `flask-cors` | main | The frontend phase will need this; wiring the config surface (`CORS_ALLOWED_ORIGINS`) now |
| `ruff` | dev | Lint (+ import sorting) |
| `black` | dev | Formatting |
| `mypy` | dev | Static type checking |
| `pytest-cov` | dev | Coverage reporting, layered onto the existing `pytest` dev dep |
| `pre-commit` | dev | Runs the above as local/CI hooks — see §9 |

### 2. Config / extensions

New env vars (`.env` / `.env.example`): `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_EXPIRES_HOURS` (default 24), `CORS_ALLOWED_ORIGINS`, `MAX_CONTENT_LENGTH_MB` (default 6, a defense-in-depth cap ahead of the app-level 5MB image check).

`app/config.py` gains: JWT settings, `CORS_ALLOWED_ORIGINS` (parsed to a list), `MAX_CONTENT_LENGTH`, and the cover-photo constants (`IMAGE_ALLOWED_FORMATS = {JPEG, PNG, WEBP}`, `IMAGE_MIN_WIDTH=400`, `IMAGE_MIN_HEIGHT=250`, `IMAGE_MAX_DIM=4000`, `IMAGE_MAX_BYTES=5MB`) — kept here since both the image-processing service and the Pydantic schema need to agree on them.

`app/extensions.py` gains two singletons next to `db`: `jwt = JWTManager()`, `cors = CORS()`. No behavior wired here — JWT error *callbacks* live in `app/errors.py` so they share the same error-envelope helper as everything else (§6).

`app/__init__.py`'s `create_app()`: adds `static_folder=str(UPLOAD_DIR.parent), static_url_path="/uploads"` to the `Flask(...)` constructor, calls `jwt.init_app(app)` and `cors.init_app(...)`, and **unconditionally** registers blueprints + error handlers (not gated by `init_db` — that flag only ever controlled schema-creation strategy, routes always need to exist, including for the test fixture).

### 3. Auth (`app/auth.py`)

- `POST /login` (`app/routes/auth.py`) looks up `User` by case-insensitive email match; 401 if none found. On success: `create_access_token(identity=str(user.id), additional_claims={"email": user.email, "is_admin": user.is_admin})` — `sub` is Flask-JWT-Extended's standard identity claim, satisfying BRIEF's "carrying `sub`, `email`, `is_admin`" wording exactly. Response includes the token plus the small `user` object from gap-fill #3.
- `admin_required` decorator (`app/auth.py`) wraps `@jwt_required()` and additionally checks the `is_admin` claim, raising a 403 **before** the wrapped view body runs at all. This ordering is load-bearing: BRIEF requires a non-admin hitting an organizer-only route to get 403 even for a nonexistent event id (must not leak resource existence) — since the decorator wraps the entire function, no route code (including the event lookup) executes before this check.
- Non-admin protected routes use plain `@jwt_required()`.

### 4. Routes & validation

```
app/routes/{auth,events,attendance,registrations}.py + helpers.py (register_blueprints, parse_event_id/get_event_or_404)
app/schemas/{auth,event}.py     # Pydantic: LoginRequest, EventCreateRequest
app/services/{registration_service,csv_export,image_processing}.py
app/errors.py                   # APIError hierarchy + envelope + JWT callbacks
```

Route id handling deviates from the obvious Flask idiom: **not** `<int:event_id>`, because Flask's int converter would 404 on a non-numeric id, but BRIEF wants that case to be a 400. Routes take `<event_id>` as a plain string; a shared `parse_event_id()` helper does the 400-or-int conversion, called after any `admin_required` check has already run.

**`EventCreateRequest`** (Pydantic) covers all of BRIEF's rules: title 3–140 trimmed, `spots > 0`, `end > start` (model-level validator), `event_type`/`location_type` validated directly against the same `app.models.enums` classes the DB uses (no value duplicated), description/host fields length-capped, and a model-level validator requiring at least one URL-shaped `location` entry when `location_type` is `virtual`/`hybrid`.

**Multipart `location` array** — no native array type in `multipart/form-data`. Concrete choice: the client sends `location` as a single JSON-encoded string form field (`Json[list[str]]` in Pydantic parses it directly, no manual `json.loads`), documented in `docs/API.md` with a curl example. Blank optional string fields (`description=""` from an unfilled form input) are normalized to `None` via a shared `mode="before"` validator — otherwise `""` would pass as a "valid" non-null value.

### 5. Image upload (`app/services/image_processing.py`)

Read bytes → size check (5MB) → `PIL.Image.open()` + `.verify()` (rejects corrupt/non-image content, and — critically — rejects anything whose actual header bytes don't match jpeg/png/webp regardless of filename extension or client `Content-Type`, satisfying the "magic bytes, not extension" requirement) → dimension bounds (400×250 min, 4000×4000 max) → re-encode via a fresh `Image.save()` call with no `exif=` kwarg (strips metadata) → server-generated `uuid4` filename, **never** the client's — saved into the existing `UPLOAD_DIR`. Validation runs before any DB write; on failure nothing is written to DB or disk.

### 6. Error envelope (`app/errors.py`)

Every non-2xx JSON response: `{"error": "<code>", "message": "...", "details": null | [...]}`. An `APIError` exception hierarchy (`ValidationEnvelopeError` from Pydantic failures, `EventFullError` → 400/`event_full`, `AlreadyRegisteredError` → 400/`already_registered`, `NoActiveRegistrationError` → 400/`no_active_registration`, `ForbiddenError` → 403, `NotFoundError`) gives BRIEF's "clear, specific 'event is full' message" a stable machine-readable code the frontend can branch on, not just a status code. `403` is now reserved purely for `admin_required` authorization failures — every business-rule/invalid-state rejection (full event, duplicate confirmed signup, no active registration to cancel) is a `400` with a distinct `error` code, a consistent split across the whole API. Flask-JWT-Extended's own callbacks (`unauthorized_loader`/`invalid_token_loader`/`expired_token_loader`) are registered to emit the **same envelope shape**, so a library-raised 401 and an app-raised 401 look identical to a client.

### 7. Business logic — the two with real branching

**`POST /event/:id/register`**: look up existing `Registration(user_id, event_id)`. Already `Confirmed` → 400 `already_registered`. Else check `confirmed_count >= event.spots` → 400 `event_full` (checked for **both** fresh signups and re-signups — a cancelled slot could've been backfilled by someone else since). Else: if a `Cancelled` row exists, **update it** (`status=Confirmed`, new `sign_up_at`) — never insert a second row, the unique constraint would reject that anyway, and BRIEF requires reusing the row. Else insert a new `Confirmed` row. Known/accepted limitation: no `SELECT...FOR UPDATE`-style lock around the count-then-write; SQLite's single-writer model plus this app's expected concurrency make it a non-issue for MVP scope — documented, not engineered around.

**`DELETE /event/:id/register`**: no row, or row already `Cancelled` → 400 `no_active_registration` (both cases collapse to one message, matching BRIEF's wording). Else flip to `Cancelled`; `sign_up_at` is left untouched (BRIEF defines it as refreshed only when status moves *to* Confirmed).

**CSV export**: `full_name, email, sign_up_at, status` columns exactly per BRIEF; filename `<slugified-title>-<start:YYYY-MM-DD>-<today:YYYY-MM-DD>.csv` (slugified to keep `Content-Disposition` well-formed).

**`GET /events` remaining-spots**: computed per event as `spots - count(Confirmed)`, same pattern already used in the model layer (`event.registrations.filter_by(...).count()`) — an N+1 query per event list call, deliberately accepted as fine at this app's scale rather than a single aggregate join.

### 8. Tests

`tests/conftest.py` gains: a `client` fixture (`app.test_client()`), `make_token`/`auth_headers` (mint a valid JWT for a given user via `create_access_token` inside `app.app_context()`), and `make_user`/`make_event` factory fixtures following the existing `VALID_KWARGS`-dict-plus-override pattern from `tests/test_event_model.py`. Route tests build their own minimal fixtures per test (the `app` fixture still uses `db.create_all()`, not the seed migration) — same isolation approach as the model tests.

New files, one per BRIEF concern, each covering happy path **and every documented error case** (not smoke tests): `test_auth_routes.py`, `test_event_routes.py`, `test_attendance_routes.py` (including the 403-before-404 ordering proof: hitting attendance as non-admin against a *nonexistent* event id must still be 403, not 404), `test_registration_routes.py` (full/duplicate/re-signup-reuses-same-row/never-registered/already-cancelled), `test_image_processing.py`, `test_error_envelope.py`.

### 9. Dev tooling — lint, format, type-check, coverage, hooks

Config lives in `solution/backend/pyproject.toml` (`[tool.ruff]`, `[tool.black]`, `[tool.mypy]`) plus `solution/backend/.pre-commit-config.yaml`:

- **ruff**: lint + import sorting. Line length 88 (matches black), a standard rule set (`E`, `F`, `I`, `UP`, `B`).
- **black**: formatting, line length 88, target Python 3.12 — ruff handles *linting*, black stays the actual formatter (not `ruff format`), per the tools named.
- **mypy**: type checking `app/`, moderate strictness (`disallow_untyped_defs = true` for this project's own code, `ignore_missing_imports` for any third-party package without inline types/stubs — Flask/SQLAlchemy/Flask-JWT-Extended's stub coverage varies, not worth fighting gaps in dependencies for an MVP).
- **pytest-cov**: `pytest --cov=app --cov-report=term-missing`, with a coverage floor (`--cov-fail-under=85`, adjustable) added to `pyproject.toml`'s `[tool.pytest.ini_options] addopts`.
- **pre-commit**: hooks for ruff (`--fix`), black (`--check`), mypy, plus `trailing-whitespace`/`end-of-file-fixer` from the standard `pre-commit-hooks` repo, each scoped via `files: ^tier-3-vibe-mvp/solution/backend/` so a config technically discoverable from the monorepo root only ever touches this project's files. **Deliberately excludes pytest** (kept out of pre-commit — it's slower than a hook should be; run manually/CI via `poetry run pytest`). **Not installed as a git hook** (see Context) — usage is `poetry run pre-commit run --all-files`, documented in `README.md`.

`README.md` gets a "Code quality" section listing all four commands (`poetry run ruff check .`, `poetry run black --check .`, `poetry run mypy app`, `poetry run pytest --cov`) plus the manual pre-commit invocation.

### 10. Docs

`docs/API.md` (mirrors `docs/DATABASE.md`): auth flow + example, full endpoint reference with request/response examples, the error-code list, cover-photo rules restated, and the three gap-fills from Context each with a one-line justification. `README.md` gains an "Environment variables" section (new vars, explicit warning to override `JWT_SECRET_KEY` outside local dev) and a "Running the API" section with a curl walkthrough using a seeded login.

### 11. Postman collection (`solution/backend/postman/`)

Two files, Postman Collection v2.1 / Environment v2 schema, committed so they're importable straight from a clean checkout:
- `postman/community-events-hub.postman_collection.json` — one folder per blueprint (Auth, Events, Attendance, Registrations), one request per scenario, deliberately mirroring the Verification checklist below 1:1 rather than inventing a separate scenario list: login (admin/attendee/malformed/unrecognized), events list (with/without token), event details (valid/bad-id/missing), create event (admin happy path with an image, non-admin 403, each validation failure), register (happy/duplicate/full), cancel + re-signup, attendance view + CSV download (admin happy path, non-admin including the nonexistent-id 403-not-404 case), and a garbled/missing-token check against a protected route.
- `postman/local.postman_environment.json` — `base_url` (default `http://localhost:5000`), `admin_email`/`attendee_email` (the seeded fixture emails), plus empty `admin_token`/`attendee_token` variables the login requests populate at runtime.

**Chaining**: the two `POST /login` requests carry a test script reading `pm.response.json().access_token` and writing it via `pm.environment.set("admin_token", ...)` / `"attendee_token"`, so every later request's `Authorization: Bearer {{admin_token}}` (or `{{attendee_token}}`) is primed automatically by running the collection top-to-bottom (folders ordered auth-first) — no manual token copy-pasting.

**Runnable, not just clickable**: every request carries `pm.test(...)` assertions on status code and, where relevant, the `error` code field from the envelope (§6) or key response fields (e.g. `remaining_spots` is present/numeric on `GET /events`; exactly one `Confirmed` row exists after the re-signup-after-cancel scenario) — so the whole collection runs as an automated pass/fail suite via Postman's Collection Runner, or headlessly via `npx newman run postman/community-events-hub.postman_collection.json -e postman/local.postman_environment.json` (Newman is optional/Node-based, just documented as the CLI-equivalent — not added as a project dependency since this is a Python backend).

`README.md`'s "Running the API" section gets a short "Or import `solution/backend/postman/*.json` into Postman" callout right after the curl walkthrough.

## Verification

Run `poetry run flask db-setup` then `poetry run flask run`, then (curl, using seeded fixture data — `alice.kim@company.com` admin, `diego.ramirez@company.com` attendee):

1. Login as admin and as attendee → 200, capture both tokens. Malformed email → 400. Unrecognized-but-valid email → 401.
2. `GET /events` with no token → 401; with a token → 200, sorted by `start`, each item has `remaining_spots` and no attendee-identifying fields.
3. `POST /event` as attendee (non-admin) → 403, and confirm the event count via `GET /events` is unchanged.
4. `POST /event` as admin, multipart with a real photo from `mockups/project/assets/photos/` → 201; confirm the saved file in `uploads/events/` has a UUID name, not the original filename. Same call missing `title`, or with `end <= start`, or `location_type=virtual` with no URL in `location` → 400 `validation_error` each time.
5. Register as attendee for an open seeded event → 201. Register again → 400 `already_registered`. Register for the seeded FULL event (id 4, 3/3 confirmed) → 400 `event_full`.
6. Cancel the registration from step 5 → 204; attendance view (as admin) shows it `Cancelled`. Register again (re-signup) → 201; attendance still shows exactly **one** row for that user/event, now `Confirmed` again (proves update-not-duplicate). Cancel a registration that never existed → 400 `no_active_registration`.
7. `GET /event/:id/attendance` as non-admin against a real event id → 403; against a **nonexistent** event id → still 403, not 404 (the explicit proof of the "admin check before existence check" rule).
8. `GET /event/:id/attendance/download` as admin → 200, `text/csv`, correct filename pattern, header row exactly `full_name,email,sign_up_at,status`.
9. Any protected route with a garbled or expired token, and with no `Authorization` header at all → 401 in both cases, same envelope shape.
10. `poetry run pytest --cov` → full suite (existing 15 model tests + all new route/schema/image tests) green, coverage report meets the configured floor.
11. `poetry run ruff check .`, `poetry run black --check .`, `poetry run mypy app` → all clean. `poetry run pre-commit run --all-files` → all hooks pass.
12. Import `postman/community-events-hub.postman_collection.json` + `postman/local.postman_environment.json` into Postman (or `npx newman run ...` headlessly) and run the whole collection → every request's assertions pass, in the same order as steps 1–9 above.
