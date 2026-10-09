# Changelog

Milestones are listed with their intended tag. Tag pushes were blocked by the build environment's git policy, so tags are created locally with `scripts/tag-milestones.sh` (it maps each tag to its commit SHA).

## v0.7.0: workbench complete
- Pages: overview, ledger with evidence detail, clocks, Definition Lab (with client-side CSV upload), maturity and guardrails, printable brief, method
- English and Arabic (right-to-left); synthetic and user-file data carry persistent banners
- CSV and JSON export of the ledger; vitest parity test against the Python golden file; CI site job

## v0.4.0: synthetic registry and sensitivity engine
- Seeded generator for a labelled synthetic registry (16 entities, ~570 items); `is_synthetic` is enforced by the schema
- 72-definition sensitivity sweep (unit x scope x threshold x guardrails) with a golden file for the TypeScript engine
- `data/synthetic/DATASHEET.md`

## v0.3.0: scoring and status engines
- `pipeline/score.py`: six-check verifiability score; checks that do not apply are excluded, not failed
- `pipeline/status.py`: deterministic status; neutral default; media-only evidence never moves a status; unit mismatches flagged, never converted
- 14 tests on real-data behaviour, including tamper tests (stale hash, bad anchor, media marked official)

## v0.2.0: real ledger and validation
- 12 sources (5 official statements, 3 official self-reports, 4 media) with extraction notes and SHA-256 hashes
- 24 commitments (federal, Abu Dhabi, national), 9 evidence items, 5 media-reported claims held apart from status
- `python -m pipeline validate | rehash | build`; anchors must appear in the stored notes

## v0.1.0: scaffold
- Python package, typed schemas (real records, derived results, synthetic registry, definitions)
- Ruff + pytest configuration, CI workflow
- `docs/LIMITATIONS.md`

## v0.0.1-plan
- `plan.md`, README, MIT license, `.gitignore`
