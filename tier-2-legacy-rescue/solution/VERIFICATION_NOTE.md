# Verification Note

**1. What the AI got wrong (or almost wrong):**
On first read, I was tempted to count the bare `except:` on line 23 as one of the "4 planted
defects" rather than the mutable-default-argument bug — the rubric explicitly buckets defects
as logic/data-handling/robustness *and* separately requires removing bare excepts as a refactor
item, so treating it as a counted bug would have been double-dipping and left me with only 3
distinct defects. Re-reading the README's bug/refactor split caught this before it went into
`BUGS.md`.

**2. How I caught it:**
Every bug claim was checked against an actual run, not just static reading: I ran the original
script on `data/sample_input.csv` and hand-computed the expected counts/overdue list from the
raw CSV, then diffed against the buggy output — this is what surfaced bug 3 (Diego/Valeria
silently dropped from status counts) and bug 4 (Jorge missing from the overdue list) as real,
observable defects rather than theoretical concerns. Bug 1 (mutable default) was confirmed with
a two-call repro script showing the engineer count doubling on the second call.

**3. How I confirmed the final result is correct:**
Ran `pytest test_report_generator.py` against `report_generator_fixed.py`: 6/6 pass. Then
copied the untouched original `report_generator.py` into a throwaway scratch directory under
the name `report_generator_fixed.py` and re-ran the identical test file against it: 5/6 tests
fail (the 6th, a completed/future-deadline sanity check, passes on both — expected, since it
isn't targeting a planted bug). Also manually ran both scripts against `data/sample_input.csv`
end-to-end and compared outputs line by line.
