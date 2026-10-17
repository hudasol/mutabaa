# Evaluation

This document has two parts. Part 1 reports three exploratory analyses that were designed after the method was built. Part 2 will report the preregistered experiments in `PREREGISTRATION.md`. Every number below is marked and checked against `results/facts.json` by `tests/test_docs_agree.py`.

## Part 1. Exploratory analyses (not preregistered)

The three analyses below (agreement with a blind second extraction, robustness of the definition finding, calibration of the score) were computed after the design was fixed and were not preregistered. No prediction was written down before they were run. Treat them as exploratory checks, not as confirmatory tests. They are recomputed by `python -m pipeline analyse` and shown on the Assurance page.

### 1a. Blind second extraction

A second extractor (a smaller language model used as an independent reader) was given only the extraction notes in `data/real/extracts/`. It was not shown the ledger, the schemas or the plan. It was asked to list every AI related commitment and every figure that appears only in media notes. Its raw output is in `data/real/blind_extraction.json`. A fixed matching rule in `pipeline/agreement.py` compares it with the ledger.

| Check | Result |
| --- | --- |
| Items listed by the blind pass | {agreement.blind_items} |
| Ledger commitments the blind pass also found | {agreement.recall.found} of {agreement.recall.n} ({agreement.recall.rate}, 95% bootstrap interval {agreement.recall.ci_low} to {agreement.recall.ci_high}) |
| Commitments with a number that it found | {agreement.numeric_recall.found} of {agreement.numeric_recall.n} ({agreement.numeric_recall.rate}) |
| Not found by the blind pass | {agreement.missed} |

The blind pass listed more items than the ledger has because it counted reported achievements as commitments. The ledger treats achievements as evidence. For that reason precision is not reported. The first comparison at v1.0.0 was made by hand and found one measurable target the ledger lacked (the low digital skill workforce target in S12), which was added as C25.

### 1b. Robustness of the definition finding (synthetic)

Synthetic registries only. Over {robustness.registries} generated registries, the same 50% target is met under some definitions and missed under others in {robustness.flip_rate} of them ({robustness.flip_rate.low} at low adoption, {robustness.flip_rate.mid} at mid, {robustness.flip_rate.high} at high). The maturity threshold explains about {robustness.effect.threshold} of the variance across definitions, guardrails {robustness.effect.guardrails}, the unit counted {robustness.effect.unit} and the scope {robustness.effect.scope}.

### 1c. Calibration of the verifiability score (real ledger)

Moving the band cut offs by up to 10 points changes the band of at most {calibration.bands.max_changed} of {calibration.bands.n} commitments. Under {calibration.weights.draws} random weightings of the six checks the ranking keeps a median rank correlation of {calibration.weights.spearman_median} with the equal weight ranking ({calibration.weights.spearman_p05} at the 5th percentile). Two checks are rarely passed: a named way to measure ({calibration.pass_rate.measurement_source}) and no undefined terms ({calibration.pass_rate.terms_defined}).

### What Part 1 does and does not show

- It shows that a second reader working from the same notes finds most of the same commitments.
- It does not show that the notes are faithful to the web pages. Both passes read the same notes. Faithfulness to the pages is checked only by anchors, hashes and the live verifier, and by the human spot check in `docs/REVIEW_CHECKLIST.md`.
- Samples are small. Treat the agreement figures as a sanity check, not a measured accuracy.
- The second extractor is a language model used as an independent reader. This is not human validation.

## Part 2. Preregistered experiments

Not yet run. See `PREREGISTRATION.md`.
