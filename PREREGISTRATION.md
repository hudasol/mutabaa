# Preregistration: experiments for Mutabaa (E1 to E4 for v1.5.0, E5 and E6 added for v1.6.0)

Written and committed on 2026-10-18, before any code for these experiments existed and before any of them was run. The commit that adds this file precedes the commit that adds `pipeline/evaluate.py` and `results/`. Predictions below are not edited after results exist. Any change of design is recorded as a dated amendment at the end, and the original text stays.

## Who built what

The method (score, status rules, definition sweep, portfolio ranking), synthetic generator A and the specification of generator B below were all written by the same author. The real ledger was curated by the same author. A positive result here is therefore weaker evidence than the same result from an independent team, and the limitations section of `docs/EVALUATION.md` says so.

## Common rules

- One command, `python -m pipeline evaluate`, runs all four experiments and writes `results/e1.json` to `results/e4.json`. `docs/EVALUATION.md` is rendered from those files.
- Every random step takes a seed. The seeds are listed per experiment. No seed is dropped after results are seen.
- Intervals are 95 percent unless stated. Quantiles use `pipeline.stats.quantile` (linear interpolation).
- Each prediction is marked HIT or MISS in `docs/EVALUATION.md`. A prediction with several parts is a HIT only if every part holds.
- Nothing in the method is tuned on these experiments.

## E1. Does the six check score relate to an observable outcome?

**Question.** Commitments that are worded more checkably: are they more likely to have public official evidence?

**Data.** The real ledger, all commitments in `data/real/commitments.json` (n is small, about 25). This is the only real data experiment and it is underpowered.

**Outcome.** A commitment is positive when at least one evidence item in `data/real/evidence.json` lists it, passes `pipeline.status.eligible`, and comes from a source of kind `official-statement` or `official-self-report`.

**Predictor.** The score ratio from `pipeline.score.score` (passed checks over applicable checks).

**Metric.** Area under the ROC curve (AUC), computed as the Mann Whitney probability that a random positive scores above a random negative, ties counted as one half. Interval: percentile bootstrap over commitments, 2000 resamples, seed 7, resamples with only one class skipped.

**Baselines.**
1. Random: a uniform random score, seeds 1 to 20; report the mean AUC and the 2.5 and 97.5 percentiles across seeds.
2. Has a numeric target (`target_number` is not null).
3. Has a number and a dated deadline (`target_number` not null and `deadline_precision` in day, month, year).
4. Owner named (`owner` not null).

**Hypothesis.** The score relates weakly and positively to the outcome.

**Predictions.**
- P1a. The score AUC point estimate lies between 0.55 and 0.80.
- P1b. The lower end of its 95 percent interval is below 0.50 (the sample cannot separate it from chance).
- P1c. The score AUC is at least the highest AUC among baselines 2 to 4 minus 0.05.

## E2. Does the definition spread finding survive a second, independently specified generator?

**Question.** The finding "the same 50 percent target is met under some definitions and missed under others" was shown on registries from generator A (`pipeline/synth.py`). Does it hold on registries from a generator with a different dependence structure?

**Generator B (specification; the implementation in `pipeline/synth_b.py` follows this text only).**
- Inputs: a seed, a number of entities, and a profile: low, mid or high. The profile sets the mean entity latent level m = 1.0, 2.0 or 3.0 on the 0 to 4 maturity scale.
- Sectors cycle through the same eight sector names as generator A. Entity names are "Synthetic {sector} Office {letter}".
- Entity effect: u = Normal(m, 0.7) per entity.
- Entity size (heavy tailed): k = min(120, 10 + int(12 * Pareto(1.5))), where Pareto(a) is Python's `random.paretovariate(a)`.
- Operation share per entity: o = Beta(2, 5). Each item is an operation with probability o, otherwise a service. A service is citizen facing with probability 0.6, otherwise business facing. Operations are internal.
- Item latent: z = u + Normal(0, 0.6) - 0.5 if the item is an operation, else u + Normal(0, 0.6). Maturity = round(z) clipped to 0 to 4.
- Guardrails share one item latent: g = 0.5 * (z - 2) + Normal(0, 1). Each flag is true when g + Normal(0, 0.8) exceeds its cut: oversight -0.3, audit trail -0.1, UAE residency -0.8, fallback 0.1. The four flags are therefore correlated with each other and with maturity.
- Annual transactions (heavy tailed): a service has int(200 * Pareto(1.1)); an operation has 0 with probability 0.6, otherwise int(50 * Pareto(1.1)).
- Every record passes the same pydantic schema as generator A and carries `is_synthetic: true`.
- Draw order: for each entity in turn, draw u, k and o; then for each of its items draw the operation flag, the audience (services only), z, g, the four flag noises in the order listed, then transactions.

**Design.** 3 profiles, 3 sizes (8, 16, 32 entities) and seeds 1 to 60: 540 registries, the same grid as the generator A study. For each registry the 72 definition sweep from `pipeline/sensitivity.py` is computed.

**Metrics.** Flip rate (share of registries where the minimum share across definitions is below 0.5 and the maximum is at least 0.5), flip rate by profile, the 5th, 50th and 95th percentiles of the spread (maximum minus minimum share), and the mean share of variance explained by each definition axis (`pipeline.robustness.first_order_effects`). Generator A values come from `data/analysis/robustness.json`.

**Baseline.** Generator A on the same grid. The obvious competitor explanation is that the finding is an artefact of generator A's independence assumptions.

**Predictions.**
- P2a. The overall flip rate under generator B lies between 0.60 and 0.95.
- P2b. The median spread under generator B is at least 0.50.
- P2c. The maturity threshold has the largest mean variance share of the four axes under generator B.
- P2d. Under generator B the low profile flip rate is lower than the high profile flip rate.

## E3. Is the Portfolio rank movement larger than sampling noise?

**Question.** The Portfolio page counts entities whose rank moves by three places or more across six definitions. How much of that movement would appear from resampling the items alone, with no change of definition?

**Setting.** Scope "all services" (the page default). The six definitions are maturity thresholds 2, 3 and 4, each with and without required guardrails, as in `site/src/engine.ts` (`PORTFOLIO_COLS`). An entity's share is the fraction of its in scope items that qualify. Ranks are competition ranks (ties share the best rank), as on the page. The fixed reference definition is threshold 3 without guardrails.

**Observed.** For each entity, the definition range: maximum rank minus minimum rank across the six definitions.

**Noise.** 200 bootstrap resamples: in each, every entity's in scope items are resampled with replacement (same count), shares are computed under the reference definition, and all entities are ranked. An entity's noise width is the 95th minus the 5th percentile of its 200 ranks. Bootstrap seed 11.

**Metric.** The number of entities whose definition range exceeds their noise width.

**Baseline (noise only).** 200 sets of six independent resamples under the reference definition (seed 12). In each set, an entity's noise only range is its maximum rank minus minimum rank across the six resamples. Report the mean number of entities whose noise only range exceeds their noise width.

**Registries.** Primary: the committed registry `data/synthetic/registry.json`. Secondary: generator A registries with seeds 1 to 20 (16 entities, default profile), to show the spread across seeds; report the mean and range of the metric.

**Predictions.**
- P3a. On the committed registry, the number of entities whose definition range exceeds their noise width is between 3 and 9.
- P3b. On the committed registry, that number is lower than the number of entities that move by three places or more (the count the page shows).
- P3c. The noise only baseline mean is below 3 on the committed registry.

**Consequence fixed in advance.** If P3b holds, the Portfolio text is changed to say how many of the moves exceed sampling noise on the built in registry, in English and Arabic, with a dated amendment here.

## E4. Do the percentile bootstrap intervals on the Assurance page cover?

**Question.** The Assurance page reports agreement rates with percentile bootstrap intervals (`pipeline.stats.bootstrap_ci`, 2000 resamples) on about 25 binary items. Do those intervals contain the true rate about 95 percent of the time?

**Simulation.** n = 25 binary items, true rates 0.70, 0.88 and 0.95. For each rate, 20 seeds (1 to 20) times 100 runs: 2000 runs per rate. In each run, draw the 25 items, compute the percentile bootstrap interval with 2000 resamples, and the Wilson score interval (z = 1.96). Each bootstrap resample draws its success count from Binomial(25, observed rate), which has the same distribution as resampling 25 binary rows with replacement. Quantiles of the resampled rates use `pipeline.stats.quantile` at 0.025 and 0.975, as on the page.

**Metrics.** Coverage (share of runs whose interval contains the true rate) for each method and rate, with a 95 percent interval across the 20 seeds (mean plus or minus 1.96 standard errors); mean interval width.

**Baselines.** The Wilson interval is the obvious competitor. The nominal 0.95 is the reference.

**Predictions.**
- P4a. Percentile bootstrap coverage at rate 0.70 lies between 0.90 and 0.95.
- P4b. Percentile bootstrap coverage at rate 0.88 lies between 0.85 and 0.93.
- P4c. Percentile bootstrap coverage at rate 0.95 is below 0.85.
- P4d. Wilson coverage is at least 0.92 at all three rates.

**Consequence fixed in advance.** If P4b or P4c holds, the Assurance page text is changed (English and Arabic) to say that the percentile intervals are too narrow near the top of the range, and the agreement interval is also reported as a Wilson interval, with a dated amendment here.

## Part two: experiments E5 and E6 on the real ledger

Registered on 2026-10-28, after the v1.5.0 release and before any code for E5 or E6 exists and before either was run. The commit that adds this section precedes the commits that add the code and the results. The author has read the ledger, the evidence file and the extraction notes while designing these experiments, so the predictions are informed guesses and not blind ones. Both experiments use the real ledger only, no synthetic data and no language model. Part one (E1 to E4) is unchanged. Common rules above apply, and `python -m pipeline evaluate` runs all six experiments.

## E5. What does a plain rule based extractor find, compared with the curated ledger?

**Question.** Curating the ledger by reading takes effort. A rule based extractor is the obvious cheaper alternative. How much of the ledger would rules recover, and how many of the lines it flags are not commitments in the ledger?

**Units.** For each file `data/real/extracts/S*.md`, a unit is one bullet: a line that starts with `- `, joined with the following lines that start with whitespace, up to the next bullet or a blank line. Headers and the introduction are not units. Units shorter than four words are dropped. Text is lower cased and whitespace is collapsed before matching.

**Reference labels.** For a commitment and each of its anchors (`source_id`, `text`), the evidence units are the units of that source's note that contain the normalised anchor text. A unit is positive when it is an evidence unit of at least one commitment. A commitment with no evidence unit is reported as unlocated and left out of recall. Unit precision is a lower bound, because a flagged unit that is not in the ledger may still be a real commitment that was not curated.

**Extractors.** Each sees one unit of text and nothing else.
1. X0, every unit.
2. X1, the unit contains a digit.
3. X2, the unit contains a digit and one of `%`, `percent`, `aed`, `billion`, `million`, `trillion`.
4. X3, X2 and a year from 2024 to 2035, or the words `within` or `by end of`.
5. X4, the unit contains one of the whole words `will`, `target`, `aim`, `plan`, `launch`, `transform`, `establish`, `commit`.

**Metrics.** Commitment recall (located commitments with at least one positive unit flagged, over located commitments), reported overall, for commitments with a numeric target (`target_number` not null) and for the others. Unit recall, unit precision and unit F1 over positive units. The share of units flagged.

**Baselines.** X0 is the trivial upper bound on recall. Random: each unit flagged with the same probability as X2 flags units, seeds 1 to 20, mean commitment recall. Reference only, not rerun: the blind second reading in `data/real/blind_extraction.json`, whose recall is already in `data/analysis/agreement.json`.

**Predictions.**
- P5a. X2 recovers at least 0.70 of the commitments with a numeric target and at most 0.50 of the others.
- P5b. No extractor from X1 to X4 has a unit F1 above 0.45.
- P5c. X1 has unit precision below 0.50.
- P5d. The blind second reading has a higher commitment recall than X3, and X3 has a higher commitment recall than the random baseline mean. Both parts must hold.
- P5e. There are no unlocated commitments.

**Consequence fixed in advance.** If P5a holds, `docs/METHODOLOGY.md` says in one sentence that numeric rules find numeric targets and miss deliverables, citing this experiment. Nothing in the product changes, because the product does not extract.

## E6. Does the status engine keep its stated invariants, and would the checks notice a broken engine?

**Question.** The status rules promise a neutral default, that media only evidence never moves a status, and that nothing depends on the order of the evidence. The ledger has too few evidence items to learn anything about accuracy, but it can test whether the rules do what they promise.

**Data.** All 25 commitments, the evidence file and the source file in `data/real`, and the data as of date used by the build. Perturbations add evidence objects in memory only. They are never written to disk. Every added object has an id that starts with `X` and is never shown anywhere.

**Order of statuses.** `no-public-evidence` below `activity-reported` below `milestone-reported` below `target-claimed-met`. `not-checkable` is outside the order.

**Invariants**, each checked for every commitment.
- I1. With all its evidence removed, a commitment is `not-checkable` if its kind is vision, projection or assessment, and `no-public-evidence` otherwise.
- I2. Adding an evidence item from a media source whose corroboration is not `official-confirmed` leaves the status, the evidence ids and the progress ratio unchanged.
- I3. Shuffling the evidence list (seeds 1 to 20) never changes the result.
- I4. Adding an eligible official evidence item of kind activity, quantified progress (value half the target, same unit) or target met claim (value equal to the target, same unit) never lowers the status within the order, and never changes `not-checkable`.
- I5. Changing the data as of date by any number of days changes only the stale flag, never the status, and the flag is true exactly when the latest eligible evidence is more than 180 days old.

**Mutants.** Five altered copies of the engine, each checked against the same invariants. A mutant is killed when at least one invariant is violated for at least one commitment.
- M1. Media evidence counts as eligible.
- M2. Eligible evidence older than 180 days is dropped.
- M3. Only the first evidence item for a commitment is used.
- M4. With no eligible evidence the status is `not-checkable` for every kind.
- M5. The vision, projection and assessment rule is checked after the evidence rules.

**Metrics.** Violations per invariant on the real engine. Mutants killed out of five. The number of commitments with two or more eligible evidence items.

**Baseline.** The mutants are the baseline: a check that kills none of them would be worthless.

**Predictions.**
- P6a. The real engine has zero violations of every invariant.
- P6b. At least four of the five mutants are killed.
- P6c. At most three of the 25 commitments have two or more eligible evidence items.

**Consequence fixed in advance.** A violation on the real engine is fixed as a bug with a dated amendment. A surviving mutant leads to a new perturbation that kills it, added as a unit test, with a dated amendment.

## Amendments

Predictions above were not changed. The entries below record what was done after the results existed, and clarifications of details that the specification left open.

**Amendment 1, 2026-10-18 (after results).** P3b held, so the Portfolio page now states, in English and Arabic, how many entities move by more than sampling noise on the built in registry, and says that the check covers only that registry and scope. P4c held, so the Assurance page now reports a Wilson interval beside the percentile bootstrap interval for agreement, and states the coverage problem near the top of the range; `pipeline/agreement.py` gains a `wilson95` field and `data/analysis/agreement.json` was recomputed. The site payload carries the few E3 and E4 numbers that the page text uses.

**Amendment 2, 2026-10-18 (decided while writing the code; committed after the results, see amendment 3).** Details the specification did not fix: generator B gives items names by position (no random draw, so the draw order above is unchanged), and sets the entity `advancement` field to u / 4 clipped to 0 to 1 because the schema requires it; the sweep does not read it. For E2, generator A's numbers are read from `data/analysis/robustness.json`, as stated above, rather than recomputed.

**Amendment 3, 2026-10-18 (after an independent review).** What git can and cannot show. The commit that adds this file (e7584a9) precedes every commit that adds experiment code or results, and the public CI run for e7584a9 was recorded by the hosting service before the runs for those later commits. Generator B, the experiment code and the results were committed together, so git cannot show that the code was finished before its first run; amendment 2 was committed after the results. Two experiments started from numbers that already existed: generator A's flip rates (E2 baseline) and the bootstrap intervals on the Assurance page (E4). E1 is the only experiment whose outcome had not been computed before. The Python version floor was raised to 3.12 because E4 uses `random.binomialvariate`; results are unchanged.
