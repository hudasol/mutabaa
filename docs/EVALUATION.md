# Evaluation

This document has two parts. Part 1 reports three exploratory analyses that were designed after the method was built. Part 2 will report the preregistered experiments in `PREREGISTRATION.md`. Every number below is marked and checked against `results/facts.json` by `tests/test_docs_agree.py`.

## Part 1. Exploratory analyses (not preregistered)

The three analyses below (agreement with a blind second extraction, robustness of the definition finding, calibration of the score) were computed after the design was fixed and were not preregistered. No prediction was written down before they were run. Treat them as exploratory checks, not as confirmatory tests. They are recomputed by `python -m pipeline analyse` and shown on the Assurance page.

### 1a. Blind second extraction

A second extractor (a smaller language model used as an independent reader) was given only the extraction notes in `data/real/extracts/`. It was not shown the ledger, the schemas or the plan. It was asked to list every AI related commitment and every figure that appears only in media notes. Its raw output is in `data/real/blind_extraction.json`. A fixed matching rule in `pipeline/agreement.py` compares it with the ledger.

| Check | Result |
| --- | --- |
| Items listed by the blind pass | <!-- fact:agreement.blind_items -->46<!-- /fact --> |
| Ledger commitments the blind pass also found | <!-- fact:agreement.recall.found -->22<!-- /fact --> of <!-- fact:agreement.recall.n -->25<!-- /fact --> (<!-- fact:agreement.recall.rate -->88%<!-- /fact -->, 95% bootstrap interval <!-- fact:agreement.recall.ci_low -->72%<!-- /fact --> to <!-- fact:agreement.recall.ci_high -->100%<!-- /fact -->) |
| Commitments with a number that it found | <!-- fact:agreement.numeric_recall.found -->12<!-- /fact --> of <!-- fact:agreement.numeric_recall.n -->14<!-- /fact --> (<!-- fact:agreement.numeric_recall.rate -->86%<!-- /fact -->) |
| Not found by the blind pass | <!-- fact:agreement.missed -->C06, C09, C16<!-- /fact --> |

The blind pass listed more items than the ledger has because it counted reported achievements as commitments. The ledger treats achievements as evidence. For that reason precision is not reported. The first comparison at v1.0.0 was made by hand and found one measurable target the ledger lacked (the low digital skill workforce target in S12), which was added as C25.

### 1b. Robustness of the definition finding (synthetic)

Synthetic registries only. Over <!-- fact:robustness.registries -->540<!-- /fact --> generated registries, the same 50% target is met under some definitions and missed under others in <!-- fact:robustness.flip_rate -->80%<!-- /fact --> of them (<!-- fact:robustness.flip_rate.low -->40%<!-- /fact --> at low adoption, <!-- fact:robustness.flip_rate.mid -->100%<!-- /fact --> at mid, <!-- fact:robustness.flip_rate.high -->100%<!-- /fact --> at high). The maturity threshold explains about <!-- fact:robustness.effect.threshold -->53.1%<!-- /fact --> of the variance across definitions, guardrails <!-- fact:robustness.effect.guardrails -->19.6%<!-- /fact -->, the unit counted <!-- fact:robustness.effect.unit -->5.9%<!-- /fact --> and the scope <!-- fact:robustness.effect.scope -->0.5%<!-- /fact -->.

### 1c. Calibration of the verifiability score (real ledger)

Moving the band cut offs by up to 10 points changes the band of at most <!-- fact:calibration.bands.max_changed -->9<!-- /fact --> of <!-- fact:calibration.bands.n -->25<!-- /fact --> commitments. Under <!-- fact:calibration.weights.draws -->1,000<!-- /fact --> random weightings of the six checks the ranking keeps a median rank correlation of <!-- fact:calibration.weights.spearman_median -->0.94<!-- /fact --> with the equal weight ranking (<!-- fact:calibration.weights.spearman_p05 -->0.52<!-- /fact --> at the 5th percentile). Two checks are rarely passed: a named way to measure (<!-- fact:calibration.pass_rate.measurement_source -->8%<!-- /fact -->) and no undefined terms (<!-- fact:calibration.pass_rate.terms_defined -->4%<!-- /fact -->).

### What Part 1 does and does not show

- It shows that a second reader working from the same notes finds most of the same commitments.
- It does not show that the notes are faithful to the web pages. Both passes read the same notes. Faithfulness to the pages is checked only by anchors, hashes and the live verifier, and by the human spot check in `docs/REVIEW_CHECKLIST.md`.
- Samples are small. Treat the agreement figures as a sanity check, not a measured accuracy.
- The second extractor is a language model used as an independent reader. This is not human validation.

## Part 2. Preregistered experiments

Not yet run. See `PREREGISTRATION.md`.
