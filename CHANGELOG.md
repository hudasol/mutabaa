# Changelog

Milestones are listed with their intended tag. Tag pushes were blocked by the build environment's git policy, so tags are created locally with `scripts/tag-milestones.sh` (it maps each tag to its commit SHA).

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
