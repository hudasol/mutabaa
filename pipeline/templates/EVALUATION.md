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

The design, metrics, baselines, seeds and predictions were committed in `PREREGISTRATION.md` before any experiment code was committed; git history shows that commit before the ones that add `pipeline/evaluate.py` and `results/`. The code and the results were committed together, so git cannot show the order of writing and running; amendment 3 in `PREREGISTRATION.md` says what can be shown. `python -m pipeline evaluate` reruns everything and writes `results/e1.json` to `results/e6.json`. The method, generator A, the specification of generator B and the real ledger share one author.

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
| P5a | X2 recovers at least 0.70 of numeric target commitments and at most 0.50 of the others | {e5.x2.recall_numeric} and {e5.x2.recall_other} | {e5.P5a} |
| P5b | No extractor from X1 to X4 has unit F1 above 0.45 | best {e5.best_f1} | {e5.P5b} |
| P5c | X1 unit precision below 0.50 | {e5.x1.precision} | {e5.P5c} |
| P5d | Blind second reading above X3, and X3 above the random baseline mean | {e5.blind.recall}, {e5.x3.recall}, {e5.random.mean} | {e5.P5d} |
| P5e | No unlocated commitments | {e5.unlocated} | {e5.P5e} |
| P6a | Zero violations of every invariant on the real engine | {e6.violations} violations | {e6.P6a} |
| P6b | At least four of five mutants killed | {e6.killed} of {e6.mutants} | {e6.P6b} |
| P6c | At most three commitments with two or more eligible evidence items | {e6.multi_evidence} | {e6.P6c} |
| P7a | Recall of the blind second reading on the new commitments at least 75% | {e7.new.recall.found} of {e7.new.commitments} ({e7.new.recall}) | {e7.P7a} |
| P7b | Numeric recall on the new commitments at least 75% | {e7.new.numeric.found} of {e7.new.numeric.n} ({e7.new.numeric}) | {e7.P7b} |
| P7c | Recall on the new commitments lower than 88% | {e7.new.recall} against {e7.first.recall} on the first cohort | {e7.P7c} |
| P7d | At least 60% of the new sources verified on the first run | {e7.verified.first} of {e7.new.sources} ({e7.verified.first.share}) | {e7.P7d} |
| P7e | At most 15% of the new commitments in the band checkable | {e7.checkable} of {e7.new.commitments} ({e7.checkable.share}) | {e7.P7e} |
| P8a | Score AUC at least 0.55 against a later public report | AUC {e8.auc} | {e8.P8a} |
| P8b | One sided permutation p at least 0.05 | p {e8.p} | {e8.P8b} |
| P8c | Score AUC at least the better baseline minus 0.05 | baselines {e8.baseline.length} (length), {e8.baseline.digit} (a digit) | {e8.P8c} |
| P8d | Between 10% and 40% of the population has a later public report | {e8.positives} of {e8.n} ({e8.share}) | {e8.P8d} |
| P8e | Score AUC above the statement length AUC | {e8.auc} against {e8.baseline.length} | {e8.P8e} |
| P9a | Linter number presence F1 at least 0.85 | {e9.number.f1} | {e9.P9a} |
| P9b | Linter number value agreement at least 0.80 | {e9.number.value} on {e9.number.both} commitments | {e9.P9b} |
| P9c | Deadline year agreement at least 0.80 | {e9.year} on {e9.year.n} commitments | {e9.P9c} |
| P9d | Owner presence accuracy at least 0.70 | {e9.owner} (always predicting the common class gives {e9.owner.baseline}) | {e9.P9d} |
| P9e | Spearman correlation of the two ratios at least 0.60 | {e9.rho} | {e9.P9e} |
| P9f | Exact band agreement at least 0.60 | {e9.band} | {e9.P9f} |
| P9g | Linter number presence F1 above the digit baseline | {e9.number.f1} against {e9.number.digit_f1} | {e9.P9g} |

### E1. Score against an observable outcome (real ledger)

Of {e1.n} commitments, {e1.positives} have at least one eligible official evidence item. The six check score separates them with an AUC of {e1.auc} (95% bootstrap interval {e1.ci_low} to {e1.ci_high}). Simple baselines: a numeric target {e1.baseline.numeric_target}, a number and a dated deadline {e1.baseline.number_and_deadline}, an owner named {e1.baseline.owner_named}. A random score gives a mean of {e1.random.mean} across 20 seeds, with 95% of seeds between {e1.random.p025} and {e1.random.p975}. The sample is too small to separate the score from chance; the result is consistent with a weak positive relation and no more.

### E2. A second generator (synthetic)

Generator B has entity level effects, guardrail flags that share one latent and follow maturity, and heavy tailed sizes and volumes. Over {e2.b.registries} registries the verdict flips in {e2.b.flip_rate} of them (generator A: {e2.a.flip_rate}); by profile {e2.b.flip_rate.low} low, {e2.b.flip_rate.mid} mid, {e2.b.flip_rate.high} high (generator A: {e2.a.flip_rate.low}, {e2.a.flip_rate.mid}, {e2.a.flip_rate.high}). The median spread between the lowest and highest share is {e2.b.spread.median} (A: {e2.a.spread.median}). Variance shares under B: threshold {e2.b.effect.threshold}, guardrails {e2.b.effect.guardrails}, unit {e2.b.effect.unit}, scope {e2.b.effect.scope} (A: {e2.a.effect.threshold}, {e2.a.effect.guardrails}, {e2.a.effect.unit}, {e2.a.effect.scope}). The finding holds under a different dependence structure. Both generators share one author, so this tests sensitivity to assumptions, not to authorship.

### E3. Portfolio rank movement against sampling noise (synthetic)

On the committed registry, {e3.moved3} of {e3.entities} entities move by three places or more across the six definitions, but only {e3.exceed} move by more than their 90% rank interval under resampling of their own items. The noise only baseline (six resamples, no change of definition) gives a mean of {e3.noise_only_mean} such entities. Across generator A seeds 1 to 20 the number exceeding noise averages {e3.seeds.exceed_mean} (range {e3.seeds.exceed_min} to {e3.seeds.exceed_max}), against {e3.seeds.moved_mean} that move by three places or more. Definition choice does move ranks beyond noise, but for fewer entities than the page used to suggest. As fixed in advance, the Portfolio page now states this (amendment 1).

### E4. Coverage of percentile bootstrap intervals (simulation)

With 25 binary items and 2000 runs per rate, nominal 95% intervals covered the true rate as follows. Percentile bootstrap: {e4.p70.bootstrap} at 0.70, {e4.p88.bootstrap} at 0.88, {e4.p95.bootstrap} at 0.95. Wilson: {e4.p70.wilson}, {e4.p88.wilson}, {e4.p95.wilson}. Mean widths at 0.95: bootstrap {e4.p95.bootstrap.width}, Wilson {e4.p95.wilson.width}. As fixed in advance, the Assurance page now reports a Wilson interval beside the bootstrap one and states the problem (amendment 1).

### E5. Rule based extractors against the ledger (real ledger)

The extraction notes hold {e5.units} bullets. {e5.positives} of them contain an anchor of one of the {e5.located} commitments, and {e5.unlocated} commitments could not be located. Five rules each saw one bullet and nothing else: X0 flags every bullet, X1 a digit, X2 a digit with a percent or money word, X3 X2 plus a year or a deadline phrase, X4 a verb of intent (the exact rules are in `PREREGISTRATION.md`).

| Rule | Bullets flagged | Commitments recovered | With a numeric target | Others | Unit precision | Unit F1 |
|---|---|---|---|---|---|---|
| X0 every bullet | {e5.x0.flagged_share} | {e5.x0.recall} | {e5.x0.recall_numeric} | {e5.x0.recall_other} | {e5.x0.precision} | {e5.x0.f1} |
| X1 digit | {e5.x1.flagged_share} | {e5.x1.recall} | {e5.x1.recall_numeric} | {e5.x1.recall_other} | {e5.x1.precision} | {e5.x1.f1} |
| X2 digit and unit word | {e5.x2.flagged_share} | {e5.x2.recall} | {e5.x2.recall_numeric} | {e5.x2.recall_other} | {e5.x2.precision} | {e5.x2.f1} |
| X3 X2 and a date | {e5.x3.flagged_share} | {e5.x3.recall} | {e5.x3.recall_numeric} | {e5.x3.recall_other} | {e5.x3.precision} | {e5.x3.f1} |
| X4 verb of intent | {e5.x4.flagged_share} | {e5.x4.recall} | {e5.x4.recall_numeric} | {e5.x4.recall_other} | {e5.x4.precision} | {e5.x4.f1} |

Reference: the blind second reading found {e5.blind.recall} of the ledger from the same notes. The preregistered random baseline flags bullets at X2's rate and recovers {e5.random.mean} of the commitments (mean of 20 seeds).

Exploratory, added after the results existed (amendment 5 in `PREREGISTRATION.md`): random flagging at each rule's own flag rate recovers {e5.x1.random_matched} (X1), {e5.x2.random_matched} (X2), {e5.x3.random_matched} (X3) and {e5.x4.random_matched} (X4). At equal effort a digit rule is about as good as flagging bullets at random, and only the verb rule does clearly better than chance. The digit rule finds most numeric targets and few of the others, the stricter numeric rules find fewer of both, and no rule comes near the curated ledger or the blind second reading. Precision is a lower bound, because the ledger is not exhaustive.

### E6. The status engine against its invariants (real ledger)

On the {e6.commitments} real commitments, with evidence added in memory only, the engine had {e6.violations} violations of the five invariants: the neutral default (I1), media evidence never moves a status (I2), no dependence on evidence order (I3), more official evidence never lowers a status (I4), and the date only changes the stale flag (I5). The same checks were run against five altered copies of the engine. Killed: {e6.killed} of {e6.mutants}. Which invariant caught each: M1 (media counts) {e6.mutant.M1}; M2 (old evidence dropped) {e6.mutant.M2}; M3 (first evidence only) {e6.mutant.M3}; M4 (neutral default replaced) {e6.mutant.M4}; M5 (rule order swapped) {e6.mutant.M5}. Only {e6.multi_evidence} commitments have two or more eligible evidence items, so order and tie rules are tested mostly through the in memory perturbations and not through the data.

### E7. The extended ledger (v1.7.0)

The ledger grew from 25 commitments and 14 sources to {e7.new.commitments} more commitments from {e7.new.sources} more sources. The blind second reading found {e7.new.recall.found} of the new commitments (95% Wilson interval {e7.new.recall.ci_low} to {e7.new.recall.ci_high}), above the {e7.first.recall} it reached on the first cohort, so P7c is a miss. Two things limit how far that figure can be read. The blind reader read the same extraction notes as the first reader, so it measures consistency of reading, not faithfulness to the pages. The notes for the new cohort were also written to a more regular template than the first cohort, which probably makes them easier to read twice. We did not test that explanation. Of the new sources, {e7.verified.first} of {e7.new.sources} were verified on the first run of `verify-live`; the rest were unreachable pages or expectations that paraphrased the page, and were corrected afterwards as recorded in `docs/DECISIONS_OVERNIGHT.md`. After the corrections {e7.verified.now} of {e7.new.sources} are verified; that figure is not a prediction result. {e7.checkable} of the new commitments reach the band checkable, which supports the finding that most public commitments are not yet checkable as written.

### E8. Does the score predict a later public report? (validity study)

Population: the {e8.n} commitments with a deadline before 30 June 2026. The scores were frozen and committed before any outcome was searched (`data/e8/frozen_scores.json`). The outcome is a dated official document on the same measure, found with a fixed search protocol; {e8.positives} commitments have one and {e8.negatives} do not. The score has AUC {e8.auc} (95% bootstrap interval {e8.ci_low} to {e8.ci_high}), the statement length baseline has {e8.baseline.length} and the digit baseline {e8.baseline.digit}. The one sided permutation p is {e8.p}. We had predicted that the sample was too small to separate the score from chance (P8b); that prediction was a miss, because the p value is below 0.05.

This is not strong evidence, for four reasons. First, the interval runs from {e8.ci_low} to {e8.ci_high}, so the lower end is barely above chance. Second, the search tool's shared budget ran out during the completion pass, so {e8.searches.not_run} of the registered searches were never run and only {e8.full.negatives} of the {e8.negatives} commitments with no report had all eight; outcome 0 means that no qualifying document was found with the searches that ran, not that none exists. Third, two exploratory analyses, not predicted, point different ways. Counting every positive that carries a recorded doubt as 0 leaves {e8.strict.positives} positives and gives AUC {e8.strict.auc} (p {e8.strict.p}). Keeping only the commitments that are positive or fully searched leaves {e8.full.n} commitments and gives AUC {e8.full.auc} (p {e8.full.p}). The first raises the estimate, the second removes the signal, which is what a fragile result looks like. Fourth, ten of the twelve positives come from the press office of one government, so the result may describe how that office reports and not commitments in general.

### E9. Does the linter recover what the ledger records?

The linter reads only the English statement of each of the {e9.n} commitments, with the rules frozen at the hash in `PREREGISTRATION.md`. Number presence: F1 {e9.number.f1} (precision {e9.number.precision}, recall {e9.number.recall}) against {e9.number.digit_f1} for a plain digit test. Where both find a number, the value is the same in {e9.number.value} of {e9.number.both} commitments. The deadline year agrees in {e9.year} of {e9.year.n} dated commitments. The linter finds an owner where the ledger has one with accuracy {e9.owner}, below the {e9.owner.baseline} of a constant guess, and the two scores correlate at {e9.rho}, so P9d and P9e are misses. The owner patterns are probably too narrow for the way the ledger names owners (we did not test this); the rules stay frozen and a fix would be a new, labelled version. The measurement source field is rare in the ledger, so it is reported without a prediction: the linter and the ledger agree on {e9.source.tp} commitments, the linter flags {e9.source.fp} the ledger does not, and misses {e9.source.fn}.

### The misses, explained

- **P4a and P4b.** We expected the percentile bootstrap to fall short of 95% at moderate rates. It did not: at 0.70 and 0.88 it covered at or slightly above the nominal level. Our expectation came from the general result that percentile intervals under cover in small samples. A likely explanation, which we have not tested, is that with 25 binary items the bootstrap distribution moves in steps of 1/25 and the interval ends include whole steps, which adds coverage. The failure is concentrated where we also predicted it, near the top of the range, where a run with all successes gives an interval of zero width. The prediction was wrong at moderate rates and is kept as a miss.
- **P5a.** X2 recovered {e5.x2.recall_numeric} of the commitments with a numeric target, below the 0.70 we expected, and none of the others as predicted. We expected a rule that asks for a digit and a percent or money word to find most numeric targets. It misses targets stated as counts (solutions, agents, employees, jobs), a rank, and a target written in words (full adoption). The prediction was too optimistic about the rule and is kept as a miss.
- **P5d.** The blind second reading ({e5.blind.recall}) is above X3 ({e5.x3.recall}) as expected, but X3 is below the random baseline mean ({e5.random.mean}), so the two part prediction fails. The registered baseline flags bullets at X2's rate, about twice X3's rate, so the comparison favours chance. The exploratory matched rate comparison above shows the same direction at equal effort: X3 asks for a digit, a unit word and a date in one bullet, and the notes often state a target and its date in separate bullets (a likely reason that we have not tested).

### Limitations of Part 2

- E1 has 25 commitments and only a handful of positives. Its interval is wide and the outcome (public official evidence) is itself curated by the author who curated the fields the score reads.
- E2 and E4 were not blind: generator A's flip rates and the Assurance page bootstrap intervals existed before the predictions were written. E1 is the only experiment whose outcome had not been computed before.
- E2 and E3 use synthetic registries from generators written by the author of the method. They show that the findings do not depend on one set of generator assumptions; they say nothing about any real entity or real registry.
- E3 measures noise by resampling items within an entity, which assumes the items are a sample from a larger population of similar items. If an office's registry is complete, a rank change has no sampling noise, but it still has measurement noise in the maturity ratings, which this experiment does not model.
- E4 simulates independent binary items with a fixed rate. Real agreement items are not exchangeable, so real coverage may differ.
- E5 uses the extraction notes as its text, not the source pages, and the notes were written by the same process that made the ledger. The rules are the simplest a developer would write; a better extractor is possible and was not tried. Unit precision is a lower bound.
- E8 has {e8.n} commitments and {e8.positives} positives, outcomes searched by language model readers with a web search tool whose shared budget ran out, one office supplying most positives, and a score whose fields were extracted by the same process that made the ledger. It does not show that verifiable wording causes reporting.
- E9 compares the linter with fields that the same author curated from the same pages, so the two are not independent. It measures agreement, not accuracy.
- E7 uses one blind reader that is a language model, a single run, and notes written by the same author as the ledger. A human reader may find fewer commitments. Commitments were chosen from official pages that state targets, which favours the numeric ones.
- E6 tests that the rules do what they promise on 25 commitments and perturbations that we wrote. It says nothing about whether the rules are the right ones, and nothing about accuracy, because no gold labels exist for status.
