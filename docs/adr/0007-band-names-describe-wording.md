# ADR 0007: Band names describe the wording

## Status
Accepted.

## Context
The verifiability score in `pipeline/score.py` applies six yes or no checks to each commitment and places it in one of three bands by the share of applicable checks passed: 80% or more, 50% or more, or less. The code identifiers for the bands are `checkable`, `partly-checkable` and `not-yet-checkable`, and the interface originally used them as labels. A simulated review (`docs/reviews/01-executive-office-lens.md`, finding A8) noted that a label such as "not yet checkable" reads as a verdict on the entity that owns the commitment, while the score only describes how the commitment is worded.

## Options considered
1. Keep the identifiers as labels and explain them in a help text.
2. Drop the bands and show the raw ratio only.
3. Keep the identifiers in code and data, and give the bands interface labels that describe the wording of a commitment.

## Decision
We chose option 3. The interface labels are "Fully specified", "Partly specified" and "Under-specified" (`site/src/i18n.ts`), with a one line "how to read this" note beside them. The code identifiers stay unchanged so that stored results and tests remain stable. The ledger also shows the six individual marks, not only the band, because the calibration analysis found that small moves in the cut offs change the band of some commitments.

## Consequences
- The labels say what is missing from a statement (a number, a unit, a dated deadline, an owner, a way to measure, defined terms) and make no claim about performance or effort.
- A check that does not apply to a kind of commitment is excluded, not failed, so deliverables and assessments are not marked down for lacking a number.
- The identifiers and the labels differ, so documentation has to name both where it refers to the code.
- The cut offs and equal weights remain choices made for this project. They are labelled as a proposal, and their sensitivity is reported on the Assurance page.
