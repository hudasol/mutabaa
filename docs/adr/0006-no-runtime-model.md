# ADR 0006: No model at runtime

## Status
Accepted.

## Context
Scores, statuses and the Definition Lab results are read as statements about public commitments. A reader must be able to ask why a commitment has a given score or status and get the same answer every time. A model that judged evidence at runtime would give answers that are hard to reproduce, hard to audit and dependent on a service outside the user's control. It would also need network access and credentials, which conflicts with ADR 0001.

## Options considered
1. Call a language model at runtime to classify evidence, assign statuses or summarise sources.
2. Use a model only during data collection, and apply written, deterministic rules for everything that produces an output.
3. Use no model anywhere, including collection.

## Decision
We chose option 2. Extraction during collection was model assisted, as stated in `docs/LIMITATIONS.md`, and its output is stored as extraction notes that are hashed and validated like any other curated input. Everything that produces an output is rule based: the six checks in `pipeline/score.py`, the ordered rules in `pipeline/status.py`, the sweep in `pipeline/sensitivity.py` and its mirror in `site/src/engine.ts`. No model runs in the pipeline build or in the browser.

## Consequences
- The same inputs always give the same scores, statuses and sweep results, and committed results are tested against a fresh run.
- Every rule is written down in code and in `docs/METHODOLOGY.md`, so a reader can argue with a specific rule rather than with an opaque judgement.
- Rules are blunt. They cannot read nuance in a statement, and some edge cases are settled during curation instead. The calibration and agreement analyses on the Assurance page report where this matters.
- Output quality still depends on the collection step. Agreement between two extraction passes is reported in `docs/EVALUATION.md` as a consistency check, not as independent human validation.
