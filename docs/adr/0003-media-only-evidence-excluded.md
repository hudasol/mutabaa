# ADR 0003: Media only evidence is excluded from status

## Status
Accepted.

## Context
Some progress figures circulate in secondary reporting but do not appear in the official statement they are attributed to. Secondary media can also repeat one another, and one secondary source in the dataset states that it was produced with AI assistance. If such figures moved a status, the ledger would present unconfirmed numbers with the weight of an official record.

## Options considered
1. Treat all sources equally and let any reported figure move a status.
2. Weight sources by type and combine them into a confidence score.
3. Let only evidence from official sources, or media evidence that an official source confirms, move a status, and keep everything else in a separate register.

## Decision
We chose option 3. Every source has a kind: `official-statement`, `official-self-report`, `secondary-media` or `third-party` (`pipeline/schemas.py`). Every evidence item and claim has a corroboration label: `official-confirmed`, `single-source` or `not-in-official-statement`. The function `eligible()` in `pipeline/status.py` excludes evidence from a `secondary-media` source unless it is `official-confirmed`. The validator in `pipeline/validate.py` rejects a media source marked `official-confirmed` and an official source marked otherwise, so the label cannot be used to bring media evidence back in.

Media figures are kept in the claim register (`data/real/claims.json`) with the label that describes what was checked, and they are shown apart from status.

## Consequences
- A status can be more cautious than press coverage suggests. This is intended.
- Excluded evidence is listed by identifier in each status result, so the exclusion is visible rather than silent.
- A commitment sourced only from secondary media produces a validation warning, and one sourced only from AI assisted material is a validation error.
- When an official source later confirms a media figure, the evidence has to be added again from the official source. The claim register shows which figures are waiting for that.
