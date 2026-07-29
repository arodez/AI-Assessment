# Verification Note

## Flows tested

All three were driven through the real browser UI (Playwright against the
running app, not raw `curl`), with screenshots and console/network checks:

**(a) Successful sign-up:** Created "Roomy Workshop" (capacity 5), signed up
`ALICE@example.com` as "Alice Example." Got `201` and "Signed up
successfully.", spots remaining dropped from 5 to 4.

**(b) Rejection when full:** Created "Tiny AMA" (capacity 1), signed up one
attendee, then attempted a second sign-up (`bob@example.com`). Server
returned `409 {"error":"full","message":"This event is full."}`; the
client-side form is also removed once an event shows 0 spots remaining.

**(c) Rejection of a duplicate email:** Signed up `alice@example.com` for
"Roomy Workshop," then attempted `alice@example.com` again (and confirmed the
check is case-insensitive by using `ALICE@example.com` the first time and
lowercase the second). Got `409 {"error":"duplicate","message":"This email is
already signed up for this event."}`.

Also exercised: overlap-confirm flow (creating an event at the same time as
an existing one triggers a confirm dialog before creating anyway), malformed
email, empty title, negative/zero capacity, past event date (all rejected
with `400` and a clear message), CSV export, and confirmed the public
`/api/events` response never contains attendee emails.

## 1. What the AI got wrong (or almost wrong)

Three real mistakes. The first two were caught by driving the app with an
automated headless browser; the third was caught by the product owner doing
their own manual pass in a real browser — proof that automated checks alone
weren't enough:

**Mistake 1 — success message was invisible in practice.** The RSVP form
showed a success message, then immediately called `loadEvents()` to refresh
the list. `loadEvents()` synchronously wiped the entire container
(`container.textContent = 'Loading…'`) in the same tick, before the browser
ever painted the success message — so a real user would never see it flash
by. A Playwright `waitForSelector('.message.success')` timing out (despite
the server returning `200` and the attendee actually being recorded) is what
exposed it — the request worked, the confirmation just never rendered.

**Mistake 2 — double-escaped HTML output.** The first pass escaped HTML
entities server-side *and* rendered everything client-side via `textContent`
(which is already XSS-safe on its own). The result: any title with special
characters displayed as broken literal entities, e.g. an event titled with a
`<script>` payload rendered on the public page as the literal text
`&lt;script&gt;...` instead of `<script>...`. Caught visually via a
screenshot taken during the XSS test — the payload never executed either
way, but the output was wrong. Removed the redundant server-side escaping,
keeping `textContent` as the single sanitization layer.

**Mistake 3 — attendee sign-up times displayed 6 hours off.** The product
owner manually tested the app (local time 10:04 AM) and noticed the
organizer view showed the sign-up as happening at "4:03 PM." Root cause:
`created_at` columns defaulted to SQLite's `datetime('now')`, which returns
**UTC** but formatted as `"2026-07-29 16:03:00"` — space-separated, no `Z`.
The browser's `new Date(...)` parses that non-ISO format as if it were
*already local time* (no conversion applied), so the raw UTC value got
displayed unconverted, off by exactly the local UTC offset. A related latent
bug from the same root cause: the public list's `WHERE event_date >=
datetime('now')` compared a proper ISO string (with `T`/`Z`) against that
same space-separated `datetime('now')` value as plain text — since `'T'`
sorts after `' '` in ASCII, an event dated *earlier today* that had already
passed could still incorrectly sort as "upcoming." Fixed both by switching
every "now" reference to `strftime('%Y-%m-%dT%H:%M:%fZ', 'now')`, matching
the ISO format used everywhere else in the app.

## 2. How I caught it

Mistakes 1 and 2 were caught by driving the actual running app end-to-end
with a headless browser and screenshotting each step, not by reading the
code or trusting API responses alone — mistake 1 in particular would have
looked "correct" from the API's point of view (200, right message body)
while being broken for a real user. Mistake 3 was caught by the product
owner's own manual testing pass, comparing the app's displayed time against
their actual local clock — a discrepancy neither of my automated checks
would have surfaced, since they only asserted formatting/ordering
correctness relative to whatever the server considered "now," not
correctness against a real external clock.

## 3. How I confirmed the final result is correct

Re-ran the full Playwright script after fixes 1 and 2 against a freshly
reset SQLite database: success message now stays visible for ~1.5s before
the list refreshes (screenshot confirms it), and the XSS-payload title now
renders as plain, literal text matching what was typed, with `window.__xss`
never set — confirming the script still doesn't execute after removing the
redundant escaping. For fix 3, inserted a fresh attendee row and directly
compared `new Date(row.created_at).toLocaleString()` against
`new Date().toLocaleString()` at insert time — they matched exactly. Also
confirmed the same-day ordering fix by inserting one event 1 hour in the
past and one 5 hours in the future on the same calendar day: the public list
now correctly shows only the future one.
