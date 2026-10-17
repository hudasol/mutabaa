# Evaluation

This document has two parts. Part 1 reports three exploratory analyses that were designed after the method was built. Part 2 reports the preregistered experiments in `PREREGISTRATION.md`, with each prediction marked HIT or MISS. Every number below is marked and checked against `results/facts.json` by `tests/test_docs_agree.py`.

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

The design, metrics, baselines, seeds and predictions were committed in `PREREGISTRATION.md` before any experiment code existed; git history shows that commit before the one that adds `pipeline/evaluate.py` and `results/`. `python -m pipeline evaluate` reruns everything and writes `results/e1.json` to `results/e4.json`. The method, generator A, the specification of generator B and the real ledger share one author.

### Predictions and results

| Id | Prediction | Result | Verdict |
|---|---|---|---|
| P1a | Score AUC between 0.55 and 0.80 | AUC {e1.auc} | {e1.P1a} |
| P1b | Lower end of the 95% interval below 0.50 | interval {e1.ci_low} to {e1.ci_high} | {e1.P1b} |
| P1c | Score AUC at least the best simple baseline minus 0.05 | baselines {e1.baseline.numeric_target}, {e1.baseline.number_and_deadline}, {e1.baseline.owner_named} | {e1.P1c} |
| P2a | Flip rate under generator B between 0.60 and 0.95 | {e2.b.flip_rate} | {e2.P2a} |
| P2b | Median spread under generator B at least 0.50 | {e2.b.spread.median} | {e2.P2b} |
| P2c | Maturity threshold has the largest variance share under B | largest: {e2.top_axis_b} | {e2.P2c} |
| P2d | Low profile flips less often than high profile under B | {e2.b.flip_rate.low} against {e2.b.flip_rate.high} | {e2.P2d} |
| P3a | Entities exceeding noise between 3 and 9 (committed registry) | {e3.exceed} of {e3.entities} | {e3.P3a} |
| P3b | Fewer entities exceed noise than move by three places or more | {e3.exceed} against {e3.moved3} | {e3.P3b} |
| P3c | Noise only baseline mean below 3 | {e3.noise_only_mean} | {e3.P3c} |
| P4a | Bootstrap coverage at rate 0.70 between 0.90 and 0.95 | {e4.p70.bootstrap} | {e4.P4a} |
| P4b | Bootstrap coverage at rate 0.88 between 0.85 and 0.93 | {e4.p88.bootstrap} | {e4.P4b} |
| P4c | Bootstrap coverage at rate 0.95 below 0.85 | {e4.p95.bootstrap} | {e4.P4c} |
| P4d | Wilson coverage at least 0.92 at all three rates | {e4.p70.wilson}, {e4.p88.wilson}, {e4.p95.wilson} | {e4.P4d} |

### E1. Score against an observable outcome (real ledger)

Of {e1.n} commitments, {e1.positives} have at least one eligible official evidence item. The six check score separates them with an AUC of {e1.auc} (95% bootstrap interval {e1.ci_low} to {e1.ci_high}). Simple baselines: a numeric target {e1.baseline.numeric_target}, a number and a dated deadline {e1.baseline.number_and_deadline}, an owner named {e1.baseline.owner_named}. A random score gives a mean of {e1.random.mean} across 20 seeds, with 95% of seeds between {e1.random.p025} and {e1.random.p975}. The sample is too small to separate the score from chance; the result is consistent with a weak positive relation and no more.

### E2. A second generator (synthetic)

Generator B has entity level effects, guardrail flags that share one latent and follow maturity, and heavy tailed sizes and volumes. Over {e2.b.registries} registries the verdict flips in {e2.b.flip_rate} of them (generator A: {e2.a.flip_rate}); by profile {e2.b.flip_rate.low} low, {e2.b.flip_rate.mid} mid, {e2.b.flip_rate.high} high (generator A: {e2.a.flip_rate.low}, {e2.a.flip_rate.mid}, {e2.a.flip_rate.high}). The median spread between the lowest and highest share is {e2.b.spread.median} (A: {e2.a.spread.median}). Variance shares under B: threshold {e2.b.effect.threshold}, guardrails {e2.b.effect.guardrails}, unit {e2.b.effect.unit}, scope {e2.b.effect.scope} (A: {e2.a.effect.threshold}, {e2.a.effect.guardrails}, {e2.a.effect.unit}, {e2.a.effect.scope}). The finding holds under a different dependence structure. Both generators share one author, so this tests sensitivity to assumptions, not to authorship.

### E3. Portfolio rank movement against sampling noise (synthetic)

On the committed registry, {e3.moved3} of {e3.entities} entities move by three places or more across the six definitions, but only {e3.exceed} move by more than their 90% rank interval under resampling of their own items. The noise only baseline (six resamples, no change of definition) gives a mean of {e3.noise_only_mean} such entities. Across generator A seeds 1 to 20 the number exceeding noise averages {e3.seeds.exceed_mean} (range {e3.seeds.exceed_min} to {e3.seeds.exceed_max}), against {e3.seeds.moved_mean} that move by three places or more. Definition choice does move ranks beyond noise, but for fewer entities than the page used to suggest. As fixed in advance, the Portfolio page now states this (amendment 1).

### E4. Coverage of percentile bootstrap intervals (simulation)

With 25 binary items and 2000 runs per rate, nominal 95% intervals covered the true rate as follows. Percentile bootstrap: {e4.p70.bootstrap} at 0.70, {e4.p88.bootstrap} at 0.88, {e4.p95.bootstrap} at 0.95. Wilson: {e4.p70.wilson}, {e4.p88.wilson}, {e4.p95.wilson}. Mean widths at 0.95: bootstrap {e4.p95.bootstrap.width}, Wilson {e4.p95.wilson.width}. As fixed in advance, the Assurance page now reports a Wilson interval beside the bootstrap one and states the problem (amendment 1).

### The misses, explained

- **P4a and P4b.** We expected the percentile bootstrap to fall short of 95% at moderate rates. It did not: at 0.70 and 0.88 it covered at or slightly above the nominal level. Our expectation came from the general result that percentile intervals under cover in small samples; with 25 binary items the bootstrap distribution is lumpy (steps of 1/25) and the interval ends include whole steps, which adds coverage. The failure is concentrated where we also predicted it, near the top of the range, where a run with all successes gives an interval of zero width. The prediction was wrong at moderate rates and is kept as a miss.

### Limitations of Part 2

- E1 has 25 commitments and only a handful of positives. Its interval is wide and the outcome (public official evidence) is itself curated by the author who curated the fields the score reads.
- E2 and E3 use synthetic registries from generators written by the author of the method. They show that the findings do not depend on one set of generator assumptions; they say nothing about any real entity or real registry.
- E3 measures noise by resampling items within an entity, which assumes the items are a sample from a larger population of similar items. If an office's registry is complete, a rank change has no sampling noise, but it still has measurement noise in the maturity ratings, which this experiment does not model.
- E4 simulates independent binary items with a fixed rate. Real agreement items are not exchangeable, so real coverage may differ.
