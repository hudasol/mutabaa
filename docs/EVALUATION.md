# Evaluation

This document has two parts. Part 1 reports three exploratory analyses that were designed after the method was built. Part 2 reports the preregistered experiments in `PREREGISTRATION.md`, with each prediction marked HIT or MISS. Every number below is marked and checked against `results/facts.json` by `tests/test_docs_agree.py`.

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

The design, metrics, baselines, seeds and predictions were committed in `PREREGISTRATION.md` before any experiment code was committed; git history shows that commit before the ones that add `pipeline/evaluate.py` and `results/`. The code and the results were committed together, so git cannot show the order of writing and running; amendment 3 in `PREREGISTRATION.md` says what can be shown. `python -m pipeline evaluate` reruns everything and writes `results/e1.json` to `results/e4.json`. The method, generator A, the specification of generator B and the real ledger share one author.

### Predictions and results

| Id | Prediction | Result | Verdict |
|---|---|---|---|
| P1a | Score AUC between 0.55 and 0.80 | AUC <!-- fact:e1.auc -->0.72<!-- /fact --> | <!-- fact:e1.P1a -->HIT<!-- /fact --> |
| P1b | Lower end of the 95% interval below 0.50 | interval <!-- fact:e1.ci_low -->0.44<!-- /fact --> to <!-- fact:e1.ci_high -->0.95<!-- /fact --> | <!-- fact:e1.P1b -->HIT<!-- /fact --> |
| P1c | Score AUC at least the best simple baseline minus 0.05 | baselines <!-- fact:e1.baseline.numeric_target -->0.40<!-- /fact -->, <!-- fact:e1.baseline.number_and_deadline -->0.45<!-- /fact -->, <!-- fact:e1.baseline.owner_named -->0.68<!-- /fact --> | <!-- fact:e1.P1c -->HIT<!-- /fact --> |
| P2a | Flip rate under generator B between 0.60 and 0.95 | <!-- fact:e2.b.flip_rate -->76%<!-- /fact --> | <!-- fact:e2.P2a -->HIT<!-- /fact --> |
| P2b | Median spread under generator B at least 0.50 | <!-- fact:e2.b.spread.median -->88%<!-- /fact --> | <!-- fact:e2.P2b -->HIT<!-- /fact --> |
| P2c | Maturity threshold has the largest variance share under B | largest: <!-- fact:e2.top_axis_b -->threshold<!-- /fact --> | <!-- fact:e2.P2c -->HIT<!-- /fact --> |
| P2d | Low profile flips less often than high profile under B | <!-- fact:e2.b.flip_rate.low -->28%<!-- /fact --> against <!-- fact:e2.b.flip_rate.high -->100%<!-- /fact --> | <!-- fact:e2.P2d -->HIT<!-- /fact --> |
| P3a | Entities exceeding noise between 3 and 9 (committed registry) | <!-- fact:e3.exceed -->5<!-- /fact --> of <!-- fact:e3.entities -->16<!-- /fact --> | <!-- fact:e3.P3a -->HIT<!-- /fact --> |
| P3b | Fewer entities exceed noise than move by three places or more | <!-- fact:e3.exceed -->5<!-- /fact --> against <!-- fact:e3.moved3 -->15<!-- /fact --> | <!-- fact:e3.P3b -->HIT<!-- /fact --> |
| P3c | Noise only baseline mean below 3 | <!-- fact:e3.noise_only_mean -->1.36<!-- /fact --> | <!-- fact:e3.P3c -->HIT<!-- /fact --> |
| P4a | Bootstrap coverage at rate 0.70 between 0.90 and 0.95 | <!-- fact:e4.p70.bootstrap -->96.0%<!-- /fact --> | <!-- fact:e4.P4a -->MISS<!-- /fact --> |
| P4b | Bootstrap coverage at rate 0.88 between 0.85 and 0.93 | <!-- fact:e4.p88.bootstrap -->95.2%<!-- /fact --> | <!-- fact:e4.P4b -->MISS<!-- /fact --> |
| P4c | Bootstrap coverage at rate 0.95 below 0.85 | <!-- fact:e4.p95.bootstrap -->70.0%<!-- /fact --> | <!-- fact:e4.P4c -->HIT<!-- /fact --> |
| P4d | Wilson coverage at least 0.92 at all three rates | <!-- fact:e4.p70.wilson -->93.5%<!-- /fact -->, <!-- fact:e4.p88.wilson -->97.9%<!-- /fact -->, <!-- fact:e4.p95.wilson -->96.4%<!-- /fact --> | <!-- fact:e4.P4d -->HIT<!-- /fact --> |

### E1. Score against an observable outcome (real ledger)

Of <!-- fact:e1.n -->25<!-- /fact --> commitments, <!-- fact:e1.positives -->5<!-- /fact --> have at least one eligible official evidence item. The six check score separates them with an AUC of <!-- fact:e1.auc -->0.72<!-- /fact --> (95% bootstrap interval <!-- fact:e1.ci_low -->0.44<!-- /fact --> to <!-- fact:e1.ci_high -->0.95<!-- /fact -->). Simple baselines: a numeric target <!-- fact:e1.baseline.numeric_target -->0.40<!-- /fact -->, a number and a dated deadline <!-- fact:e1.baseline.number_and_deadline -->0.45<!-- /fact -->, an owner named <!-- fact:e1.baseline.owner_named -->0.68<!-- /fact -->. A random score gives a mean of <!-- fact:e1.random.mean -->0.47<!-- /fact --> across 20 seeds, with 95% of seeds between <!-- fact:e1.random.p025 -->0.16<!-- /fact --> and <!-- fact:e1.random.p975 -->0.74<!-- /fact -->. The sample is too small to separate the score from chance; the result is consistent with a weak positive relation and no more.

### E2. A second generator (synthetic)

Generator B has entity level effects, guardrail flags that share one latent and follow maturity, and heavy tailed sizes and volumes. Over <!-- fact:e2.b.registries -->540<!-- /fact --> registries the verdict flips in <!-- fact:e2.b.flip_rate -->76%<!-- /fact --> of them (generator A: <!-- fact:e2.a.flip_rate -->80%<!-- /fact -->); by profile <!-- fact:e2.b.flip_rate.low -->28%<!-- /fact --> low, <!-- fact:e2.b.flip_rate.mid -->99%<!-- /fact --> mid, <!-- fact:e2.b.flip_rate.high -->100%<!-- /fact --> high (generator A: <!-- fact:e2.a.flip_rate.low -->40%<!-- /fact -->, <!-- fact:e2.a.flip_rate.mid -->100%<!-- /fact -->, <!-- fact:e2.a.flip_rate.high -->100%<!-- /fact -->). The median spread between the lowest and highest share is <!-- fact:e2.b.spread.median -->88%<!-- /fact --> (A: <!-- fact:e2.a.spread.median -->80%<!-- /fact -->). Variance shares under B: threshold <!-- fact:e2.b.effect.threshold -->43.8%<!-- /fact -->, guardrails <!-- fact:e2.b.effect.guardrails -->24.9%<!-- /fact -->, unit <!-- fact:e2.b.effect.unit -->3.9%<!-- /fact -->, scope <!-- fact:e2.b.effect.scope -->0.5%<!-- /fact --> (A: <!-- fact:e2.a.effect.threshold -->53.1%<!-- /fact -->, <!-- fact:e2.a.effect.guardrails -->19.6%<!-- /fact -->, <!-- fact:e2.a.effect.unit -->5.9%<!-- /fact -->, <!-- fact:e2.a.effect.scope -->0.5%<!-- /fact -->). The finding holds under a different dependence structure. Both generators share one author, so this tests sensitivity to assumptions, not to authorship.

### E3. Portfolio rank movement against sampling noise (synthetic)

On the committed registry, <!-- fact:e3.moved3 -->15<!-- /fact --> of <!-- fact:e3.entities -->16<!-- /fact --> entities move by three places or more across the six definitions, but only <!-- fact:e3.exceed -->5<!-- /fact --> move by more than their 90% rank interval under resampling of their own items. The noise only baseline (six resamples, no change of definition) gives a mean of <!-- fact:e3.noise_only_mean -->1.36<!-- /fact --> such entities. Across generator A seeds 1 to 20 the number exceeding noise averages <!-- fact:e3.seeds.exceed_mean -->5.25<!-- /fact --> (range <!-- fact:e3.seeds.exceed_min -->2<!-- /fact --> to <!-- fact:e3.seeds.exceed_max -->11<!-- /fact -->), against <!-- fact:e3.seeds.moved_mean -->11.10<!-- /fact --> that move by three places or more. Definition choice does move ranks beyond noise, but for fewer entities than the page used to suggest. As fixed in advance, the Portfolio page now states this (amendment 1).

### E4. Coverage of percentile bootstrap intervals (simulation)

With 25 binary items and 2000 runs per rate, nominal 95% intervals covered the true rate as follows. Percentile bootstrap: <!-- fact:e4.p70.bootstrap -->96.0%<!-- /fact --> at 0.70, <!-- fact:e4.p88.bootstrap -->95.2%<!-- /fact --> at 0.88, <!-- fact:e4.p95.bootstrap -->70.0%<!-- /fact --> at 0.95. Wilson: <!-- fact:e4.p70.wilson -->93.5%<!-- /fact -->, <!-- fact:e4.p88.wilson -->97.9%<!-- /fact -->, <!-- fact:e4.p95.wilson -->96.4%<!-- /fact -->. Mean widths at 0.95: bootstrap <!-- fact:e4.p95.bootstrap.width -->0.12<!-- /fact -->, Wilson <!-- fact:e4.p95.wilson.width -->0.19<!-- /fact -->. As fixed in advance, the Assurance page now reports a Wilson interval beside the bootstrap one and states the problem (amendment 1).

### The misses, explained

- **P4a and P4b.** We expected the percentile bootstrap to fall short of 95% at moderate rates. It did not: at 0.70 and 0.88 it covered at or slightly above the nominal level. Our expectation came from the general result that percentile intervals under cover in small samples. A likely explanation, which we have not tested, is that with 25 binary items the bootstrap distribution moves in steps of 1/25 and the interval ends include whole steps, which adds coverage. The failure is concentrated where we also predicted it, near the top of the range, where a run with all successes gives an interval of zero width. The prediction was wrong at moderate rates and is kept as a miss.

### Limitations of Part 2

- E1 has 25 commitments and only a handful of positives. Its interval is wide and the outcome (public official evidence) is itself curated by the author who curated the fields the score reads.
- E2 and E4 were not blind: generator A's flip rates and the Assurance page bootstrap intervals existed before the predictions were written. E1 is the only experiment whose outcome had not been computed before.
- E2 and E3 use synthetic registries from generators written by the author of the method. They show that the findings do not depend on one set of generator assumptions; they say nothing about any real entity or real registry.
- E3 measures noise by resampling items within an entity, which assumes the items are a sample from a larger population of similar items. If an office's registry is complete, a rank change has no sampling noise, but it still has measurement noise in the maturity ratings, which this experiment does not model.
- E4 simulates independent binary items with a fixed rate. Real agreement items are not exchangeable, so real coverage may differ.
