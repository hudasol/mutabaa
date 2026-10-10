# Review 1: an AI engineer at an executive office (ADEO lens)

This is a simulated critique from the point of view of an analyst-engineer whose job is to brief leadership on whether strategic plans are being implemented. It is written from public information about such an office, not from inside knowledge. Reviewed: v1.0.0, https://mutabaa-adeoi.vercel.app/

## What I would say in the first five minutes
"Interesting idea, and the neutral default is right. But I cannot put this in front of my supervisor yet. I can't tell if the numbers are correct, I can't tell how fresh anything is, and the first thing the home page shows me is a chart of fake data."

## Findings

| # | Severity | Finding | Evidence in v1.0.0 | Why it matters to me |
|---|---|---|---|---|
| A1 | High | I cannot tell whether a figure on the page is on the source page | Quotes are checked against notes, not the live page (`docs/LIMITATIONS.md`) | If one number is wrong in a briefing, I lose the room |
| A2 | High | "No public evidence" does not say what was searched | Status text has no search scope or date | I will be asked "did you look?" and have no answer |
| A3 | High | No freshness signal | `as_of` exists on evidence but is not turned into an age; no "data as of" in the header | A 2025 figure and a 2026 figure look the same |
| A4 | High | The home page leads with synthetic data | Hero is the 72-definition strip with a violet badge | A reader who skims takes away a made-up number |
| A5 | Medium | I cannot send a colleague what I am looking at | Lab selections and filters are not in the URL | Briefing is a team activity |
| A6 | Medium | The tool tells me what is missing but not what to do about it | Missing checks are listed as labels | I need the question to put to the entity |
| A7 | Medium | Real inventories will not match your CSV template | Fixed columns only; first bad row stops the story | The upload is the feature I would demo |
| A8 | Medium | "Not yet checkable" reads as a verdict on the entity | Band names | The tool should describe the wording of a commitment, not judge a ministry; a political reader will react to the label |
| A9 | Medium | No version or hash on the brief | Print view has a date only | I need to say which version of the data a page came from |
| A10 | Low | Arabic and English can drift | No parity test | One missing string is a visible failure |
| A11 | Low | The ledger is a long flat table | No sort, no grouping | With 25 rows it is fine; with 250 it is not |

## Checklist (each item has an acceptance test)

- [x] A1 `verify-live` command: fetches each source on a networked machine, checks expected figures and the date, writes `data/real/verification.json`. Test: fixture pages pass and fail correctly; a missing figure fails.
- [x] A1 The app shows, per source, "verified on DATE" or "not yet verified against the live page". Test: renders both states.
- [x] A1 Scheduled workflow runs the verifier weekly and fails when a figure disappears. Test: workflow file parses.
- [x] A2 Search log with scope, date, result, and linked commitments. Test: validator rejects a log entry for an unknown commitment.
- [x] A2 Each commitment shows "Searched N places, last on DATE, found M items". Test: payload carries coverage.
- [x] A3 Evidence age and a staleness flag (more than 180 days). Test: engine unit test on boundary.
- [x] A3 "Data as of" in the header and the brief. Test: payload field present.
- [x] A4 Home page leads with the real finding; synthetic strip is second and labelled as an illustration. Test: screenshot review.
- [x] A5 Lab state, ledger filters and the open commitment are in the URL. Test: parse and serialise round trip.
- [x] A6 "Questions for the entity" generated per commitment, in English and Arabic, exportable. Test: every failed check yields a question; golden file.
- [x] A7 CSV column mapper and a data-quality report. Test: renamed headers can be mapped; report counts duplicates and blanks.
- [x] A8 Rename bands to describe wording ("Fully specified", "Partly specified", "Under-specified") and add a one-line "how to read this". Test: no old label left in the UI; docs updated.
- [x] A9 Payload hash and data-as-of shown in the footer and the brief. Test: hash is stable for the same data and changes when data changes.
- [x] A10 Key parity test for English and Arabic. Test: fails if a key is missing.
- [x] A11 Sortable ledger columns. Test: e2e later; unit test on sorter.

## Outcome (v1.1.0)
All items done. Evidence: 36 Python tests and 17 site tests pass; `verify-live` verified 11 of 14 sources (S10, S11, S12 unreachable, reported as such); screenshots reviewed in light, dark, Arabic and mobile. Not done: end-to-end browser test for ledger sort (unit-tested only).
