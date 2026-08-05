# Verification Note

> 5–8 lines. Honesty is graded; "the AI made no mistakes" is almost never true and reads as a red flag.

**1. What the AI got wrong (or almost wrong):**
My first attempt at testing Flow C (duplicate email rejection) was invalid evidence: I ran it against an event that Flow B had already filled to capacity, so the resulting `409` could have come from either the "event full" check or the "duplicate email" check — it didn't actually prove the duplicate logic worked. Separately, a concurrency stress test (5 simultaneous RSVPs to the same email) hung the whole test session because I forgot to bound the curl calls with `--max-time`, which was a tooling mistake on my part, not caught until the command timed out.

**2. How I caught it:**
I noticed the Flow C test shared a database/event state with the just-completed Flow B and re-read my own curl commands — the event used for Flow C had capacity 2 and was already full from two prior sign-ups, so the rejection reason was ambiguous. I re-ran Flow C in isolation against a fresh event with capacity 5, so only the duplicate-email path could possibly trigger. For the concurrency hang, I checked `ps aux` after the timeout to confirm no process was actually stuck, then re-ran with `--max-time 3` on every curl call, which resolved it.

**3. How I confirmed the final result is correct** (tests run, manual checks, sample data used):

- **Flow A — Successful sign-up:** Created an event with capacity 2. POSTed a valid RSVP (`Alice`, `alice@example.com`) → `302` redirect to `/events/1?success=1`. Confirmed via GET that "spots left" dropped from 2 to 1.
- **Flow B — Rejection when full:** Same event, added a second valid RSVP (`Bob`) → spots dropped to 0, page shows "Full". A third RSVP attempt (`Charlie`) → `409 Conflict`, response body contains "This event is already full."
- **Flow C — Rejection of duplicate email:** Isolated test on a fresh event with capacity 5. `alice@example.com` signs up successfully (`302`). A second RSVP with the same email in different casing/whitespace (`" ALICE@EXAMPLE.COM "`) → `409 Conflict`, response body contains "This email has already signed up for this event." Confirmed the event still shows only 1 signup / 4 spots left, not 2/3 — proving no duplicate row was inserted.
- **Extra (beyond the required 3):** Concurrency test — 5 simultaneous RSVP requests with the identical email against a capacity-1 event. Result: exactly 1 request succeeded (`302`), the other 4 were rejected as duplicates (`409`) — confirmed by final signup count staying at 1/1, not 5/1. This validates that duplicate prevention relies on the database's `UNIQUE` index inside a transaction, not just an app-level pre-check that could race.
