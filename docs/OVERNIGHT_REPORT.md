# Overnight report: v1.7.0 to v1.9.0

Author: Huda Mueen. This report covers the unattended upgrade of Mutabaa from 25 to 96 commitments and the work that followed. Every number below is marked so that `tests/test_docs_agree.py` checks it against `results/facts.json`. Decisions taken without consultation are in [`DECISIONS_OVERNIGHT.md`](DECISIONS_OVERNIGHT.md) (D1 to D16).

## What was built

| Package | Result | Release |
|---|---|---|
| Ledger | <!-- fact:commitments.count -->96<!-- /fact --> commitments from <!-- fact:sources.count -->62<!-- /fact --> public sources, with notes, hashes and anchors; first run of the live verifier kept | v1.7.0 |
| Validity study (E8) | Preregistered; reported as fragile | v1.8.0 |
| Wording linter | `mutabaa lint` and `#/lint`, fixed rules, golden files between Python and the browser, E9 | v1.8.0 |
| Weekly source check | `mutabaa monitor` and a scheduled workflow that edits no ledger record | v1.8.0 |
| Definition Card | Schema, validator, command, form, three synthetic examples | v1.8.0 |
| Glossary and Arabic review kit | Ten terms with a consistency test; a string table for a native reader | v1.9.0 |
| Layout and print | 320 pixel check on every page; one page summary of any ledger view | v1.9.0 |
| Security and CI | Threat model, SBOMs, read only CI token, regression and card steps | v1.9.0 |
| Independent review | 26 findings; fixes in separate commits; rejections reasoned in D16 | v1.9.0 |

## Every new prediction, graded

Hits <!-- fact:evaluation.hits -->31<!-- /fact --> of <!-- fact:evaluation.predictions -->39<!-- /fact --> across all nine experiments; <!-- fact:evaluation.misses -->8<!-- /fact --> missed. The 17 predictions registered for this upgrade follow, with the misses given the same space as the hits.

| Id | Prediction | Result | Verdict |
|---|---|---|---|
| P7a | Recall of the blind second reading on the new commitments at least 75% | <!-- fact:e7.new.recall -->100%<!-- /fact --> | <!-- fact:e7.P7a -->HIT<!-- /fact --> |
| P7b | Numeric recall at least 75% | <!-- fact:e7.new.numeric -->100%<!-- /fact --> | <!-- fact:e7.P7b -->HIT<!-- /fact --> |
| P7c | Recall on the new commitments lower than on the first cohort | <!-- fact:e7.new.recall -->100%<!-- /fact --> against <!-- fact:e7.first.recall -->88%<!-- /fact --> | <!-- fact:e7.P7c -->MISS<!-- /fact --> |
| P7d | At least 60% of the new sources verified on the first run | <!-- fact:e7.verified.first.share -->85%<!-- /fact --> | <!-- fact:e7.P7d -->HIT<!-- /fact --> |
| P7e | At most 15% of the new commitments in the band checkable | <!-- fact:e7.checkable.share -->6%<!-- /fact --> | <!-- fact:e7.P7e -->HIT<!-- /fact --> |
| P8a | Score AUC at least 0.55 against a later public report | <!-- fact:e8.auc -->0.69<!-- /fact --> | <!-- fact:e8.P8a -->HIT<!-- /fact --> |
| P8b | One sided permutation p at least 0.05 | <!-- fact:e8.p -->0.026<!-- /fact --> | <!-- fact:e8.P8b -->MISS<!-- /fact --> |
| P8c | Score AUC at least the better baseline minus 0.05 | <!-- fact:e8.auc -->0.69<!-- /fact --> against <!-- fact:e8.baseline.length -->0.60<!-- /fact --> | <!-- fact:e8.P8c -->HIT<!-- /fact --> |
| P8d | 10% to 40% of the population has a later report | <!-- fact:e8.share -->33%<!-- /fact --> | <!-- fact:e8.P8d -->HIT<!-- /fact --> |
| P8e | Score AUC above the length baseline | <!-- fact:e8.auc -->0.69<!-- /fact --> against <!-- fact:e8.baseline.length -->0.60<!-- /fact --> | <!-- fact:e8.P8e -->HIT<!-- /fact --> |
| P9a | Number presence F1 at least 0.85 | <!-- fact:e9.number.f1 -->0.91<!-- /fact --> | <!-- fact:e9.P9a -->HIT<!-- /fact --> |
| P9b | Number value agreement at least 0.80 | <!-- fact:e9.number.value -->0.95<!-- /fact --> | <!-- fact:e9.P9b -->HIT<!-- /fact --> |
| P9c | Deadline year agreement at least 0.80 | <!-- fact:e9.year -->0.94<!-- /fact --> | <!-- fact:e9.P9c -->HIT<!-- /fact --> |
| P9d | Owner presence accuracy at least 0.70 | <!-- fact:e9.owner -->0.30<!-- /fact --> against a constant baseline of <!-- fact:e9.owner.baseline -->0.74<!-- /fact --> | <!-- fact:e9.P9d -->MISS<!-- /fact --> |
| P9e | Spearman correlation of the two ratios at least 0.60 | <!-- fact:e9.rho -->0.48<!-- /fact --> | <!-- fact:e9.P9e -->MISS<!-- /fact --> |
| P9f | Exact band agreement at least 0.60 | <!-- fact:e9.band -->0.61<!-- /fact --> | <!-- fact:e9.P9f -->HIT<!-- /fact --> |
| P9g | Number presence F1 above the digit baseline | <!-- fact:e9.number.f1 -->0.91<!-- /fact --> against <!-- fact:e9.number.digit_f1 -->0.86<!-- /fact --> | <!-- fact:e9.P9g -->HIT<!-- /fact --> |

### What the misses mean

- **P7c.** We expected the blind second reading to do worse on the new commitments. It found all of them. The likely reason is that the new notes were written with the same layout as the old ones, so the reading was easier, not that the method improved. We have not tested that.
- **P8b.** The permutation test separates the score from chance (p <!-- fact:e8.p -->0.026<!-- /fact -->), against our prediction that it would not. This is the headline of the study and also the weakest part. The interval runs from <!-- fact:e8.ci_low -->0.52<!-- /fact --> to <!-- fact:e8.ci_high -->0.85<!-- /fact -->. On the <!-- fact:e8.full.n -->18<!-- /fact --> commitments that are positive or fully searched the AUC is <!-- fact:e8.full.auc -->0.52<!-- /fact -->. <!-- fact:e8.searches.not_run -->53<!-- /fact --> registered searches never ran, and most positives come from one government's press office. An independent review found that the finder did not apply the registered tie rule; with the rule applied there are <!-- fact:e8.strict.positives -->4<!-- /fact --> positives and an AUC of <!-- fact:e8.strict.auc -->0.80<!-- /fact -->. No verdict changes (amendment 8). We read this as a weak association in a small sample, not as evidence that clearer wording causes a report.
- **P9d.** The owner rule finds an owner far less reliably than a constant guess. The frozen rule is too narrow for the many ways the sources name an owner. A better rule would be a new, labelled exploratory version, not a change to the registered one.
- **P9e.** The linter and the ledger agree on bands but rank the commitments less alike than we expected, a possible reason, which we have not tested, is that the linter reads one sentence and the ledger reads the whole note.

## Environment

Each results file has a record in `results/env/`: Python 3.13, pydantic 2.13.5, pytest 9.1.1, ruff 0.17.3, mypy 2.4.0, Node 22. Seeds are fixed inside each experiment and listed in `PREREGISTRATION.md`. CI does not diff `results/env/` because platform strings differ between machines.

## Checks at the end

- Python: ruff, mypy and pytest pass; coverage is above the 90% gate.
- Site: the unit tests, the end to end tests (axe on every page in both languages and themes, a 320 pixel check, the print view) and the bundle budgets pass.
- Frozen regression test (`tests/test_regression_frozen.py`): the score, status engine, sweep, portfolio and the results of E1 to E6 are unchanged from v1.6.0.
- Every commit is authored and committed as Huda Mueen.

## What still needs a person

| Item | Why it stays open | Prepared |
|---|---|---|
| Native Arabic review | No native speaker has read the Arabic | `docs/review_kits/arabic_review.md`, `arabic_strings.csv` |
| A person labelled gold set | The ledger was curated by one author | `docs/REVIEW_CHECKLIST.md` |
| Legal reading of the sources policy | Not a lawyer's reading | `docs/SOURCES_POLICY.md`, `docs/COMPLIANCE.md` |
| A real pilot | Needs a sponsor and real data | `docs/PILOT.md` |
| E8 by a second searcher | The outcome rests on one finder | Roadmap item |

## Tags to push

The container could not push tags. From a clone of the repository run:

```
git fetch origin
git push origin v1.7.0 v1.8.0 v1.9.0
```

v1.7.0 marks the extended ledger, v1.8.0 the commit that completes the Definition Card, and v1.9.0 the final commit of this upgrade.
