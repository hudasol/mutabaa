# Monitoring source pages

Public pages change, move or disappear. A weekly workflow (`.github/workflows/drift.yml`) checks that the sources of the ledger still show what the extraction notes rely on.

## What it does
1. Runs `python -m pipeline monitor`, which runs the live verifier over every source (robots.txt is respected; pages are fetched one at a time with a pause).
2. Compares the result with the recorded run in `data/real/verification.json`. A page is **changed** when its result differs or when the hash of its visible text differs from the recorded hash. A page is **newly unreachable** when it could not be read now but could before.
3. Writes `monitoring/drift-YYYY-MM-DD.md` and `.json`, and commits them as Huda Mueen.
4. Opens one tracking issue labelled `source-drift` only when a page changed or became unreachable. If such an issue is already open, the workflow adds a comment instead of opening another.

## What it never does
- It never changes a ledger record, a status, a score or a source hash. A person reads a changed page and decides whether a record needs a correction, through the corrections process.
- It uses no secrets and no paid service. Every action is pinned to a commit SHA.
- Pages that stay unreachable week after week are listed in the report but do not open an issue each week, to avoid noise. They are never used as evidence.

## Limits
- Only HTML pages can be checked; PDFs are recorded as not checkable.
- A hash change can be a banner or a date in the page footer. The report says what changed, not whether it matters.
- The hashes in the recorded run come from the build environment on the date of the run.

## Test
`tests/test_monitor.py` runs the comparison on recorded page text with no network: no change, a changed page, a new outage, and an old outage.
