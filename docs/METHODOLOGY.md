# Methodology

## Unit of analysis
A commitment is something an official source says a government will do, deliver, spend, expect or assess. Reported achievements are evidence, not commitments.

## Verifiability score (`pipeline/score.py`)
Six yes/no checks: a number to reach, a defined unit, a dated deadline, a named owner, a named way to measure, and no undefined terms. Deliverables and assessments need no number, so those two checks are left out for them. Bands: 80% or more checkable, 50% or more partly checkable, otherwise not yet checkable. The score describes the wording of a commitment, not performance.

## Status (`pipeline/status.py`)
1. Vision, projection and assessment: `not-checkable`.
2. Evidence from media that no official source confirms is excluded. If none is left: `no-public-evidence`.
3. A figure in the same unit as the target gives `milestone-reported` and a ratio (or `target-claimed-met` if the source claims it).
4. Otherwise `activity-reported`. A different unit is flagged and never converted.

## Definition Lab (`pipeline/sensitivity.py`, `site/src/engine.ts`)
72 definitions: 4 units, 3 scopes, 3 maturity thresholds, 2 guardrail settings. Entities and sectors count when at least half of their in-scope items qualify. The two implementations are held identical by `data/golden/sensitivity.json`.

## Provenance
Each source has a SHA-256 of its extraction note. Each commitment, evidence item and claim carries a short anchor that must appear in that note. `python -m pipeline validate` fails on a stale hash, a missing anchor, or media evidence labelled official.

## Synthetic data
See `data/synthetic/DATASHEET.md`. Synthetic and real figures are never combined.
