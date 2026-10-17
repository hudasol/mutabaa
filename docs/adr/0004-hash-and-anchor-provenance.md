# ADR 0004: Provenance by hash and anchor

## Status
Accepted.

## Context
Every real field in the ledger has to trace back to a public source. Pages change or disappear after they are read, and copying page text into the repository would republish material that belongs to its publishers. A reviewer still needs a way to find the passage a record relies on, and a way to detect a record that was edited after it was checked.

## Options considered
1. Store only the URL of each source.
2. Mirror the source pages (text, PDF or screenshots) in the repository.
3. Store a short extraction note for each source, a SHA-256 hash of that note, and short anchor phrases that must appear in the note.

## Decision
We chose option 3. Each source in `data/real/sources.json` has an extraction note in `data/real/extracts/` and a `content_hash`, the SHA-256 of the note with line endings normalised to LF (`file_hash()` in `pipeline/validate.py`, with `eol=lf` pinned in `.gitattributes`). Each commitment, evidence item and claim carries a short anchor that must appear in the note for its source. `python -m pipeline validate` fails on a stale hash, a missing anchor, an unknown reference, or media evidence labelled official.

Because anchors are checked against notes and not against the live page, `python -m pipeline verify-live` adds a second check on a networked machine: it fetches each page and looks for the figures listed in `expect_present` and for the absence of those in `expect_absent`. A page that refuses the request is reported as unreachable, never as verified.

## Consequences
- A changed note without a new hash fails validation, and a tamper test covers this (`tests/test_real_data.py`).
- No page text, images or full quotations are stored (`docs/SOURCES_POLICY.md`).
- The hash protects the wording of a note, not the source page itself. A page that changes after extraction is detected by the weekly live check, not prevented.
- The notes have not yet been reviewed by a person other than the author. This is an open item in `docs/REVIEW_CHECKLIST.md`.
