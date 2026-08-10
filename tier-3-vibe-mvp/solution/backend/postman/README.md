# Postman Collection

Importable, runnable test suite for the API — 27 requests across 5
folders (Auth, Events, Registrations, Attendance, Errors), mirroring the
manual verification checklist in `../../../PLAN-backend.md`. Every
request carries `pm.test(...)` assertions, so the whole collection runs
as an automated pass/fail suite, not just a set of examples to click
through.

## Files

- `community-events-hub.postman_collection.json` — the requests.
- `local.postman_environment.json` — `base_url` (default
  `http://localhost:5000`), the seeded `admin_email`/`attendee_email`, and
  empty `admin_token`/`attendee_token` variables the two login requests
  populate automatically.

## Running it

1. Start with a **freshly seeded** database — registration state persists
   across runs, so re-running without resetting will hit
   `already_registered` where the first run expected success:

   ```bash
   cd ..
   rm -rf instance uploads
   poetry run flask db-setup
   poetry run flask run
   ```

2. **In Postman**: File → Import both JSON files, select the "Community
   Events Hub - Local" environment (top-right), then Collection Runner →
   Run. Requests are ordered so "1. Auth" runs first and populates the
   token variables every later request depends on.

3. **Headlessly via Newman** (Node/npm; not a project dependency, just
   documented as the CLI-equivalent):

   ```bash
   npx newman run community-events-hub.postman_collection.json \
     -e local.postman_environment.json
   ```

Both were used to validate this collection during development — 27/27
requests, 70/70 assertions passing against a freshly seeded database.

## Notes

- The `image` form field on "Create event (admin, happy path)" is present
  but disabled, so the collection runs headlessly without a bundled
  binary asset — attach a file manually in the Postman GUI to also
  exercise the cover-photo upload/validation path.
- "Attendance (non-admin, NONEXISTENT event) -> still 403, not 404" is
  the explicit proof point for BRIEF's "don't leak whether the resource
  exists" rule — the admin check runs before any event lookup.
