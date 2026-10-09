# Review 3: a research scientist at an applied-research institute (TII lens)

Simulated critique, written from public information about how such groups judge claims, not from inside knowledge. Reviewed: v1.2.0.

## What I would say in the first five minutes
"Engineering is solid. I want to know which of your claims are measured and which are asserted. 'From 0% to 88%' is one synthetic registry, one seed. Your score has six equal-weight checks nobody has tested. Your second extraction is 24 items by hand. Show me the spread, the ablation and the intervals, and tell me what you still have not validated."

## Findings

| # | Severity | Finding | Evidence in v1.2.0 | Why it matters |
|---|---|---|---|---|
| C1 | High | The headline "0% to 88%" comes from one seed and one set of generator assumptions | `data/synthetic/registry.json` seed 20260423 | A reader may take a number from a generator as a result |
| C2 | High | The score has equal weights and fixed cut-offs and was never stress-tested | `pipeline/score.py` | Looks arbitrary; floor effects hide in the pass rates |
| C3 | High | Agreement with the second extraction has no interval | `docs/EVALUATION.md` (counts by hand) | n is small; point estimates mislead |
| C4 | Medium | Which definition choice drives the spread is asserted, not measured | Lab marginals only | The mechanism is the contribution; it should be decomposed |
| C5 | Medium | Definition axes have no stated rationale or mapping | Literals in code | A practitioner cannot argue with an unwritten choice |
| C6 | Medium | Structured fields were never compared with a second reading of the wording | None | Curation slips go unnoticed |
| C7 | Medium | No release process or citation metadata | Tags blocked, no `CITATION.cff` | Results cannot be cited at a version |
| C8 | Low | CSV size cap exists but is untested | `MAX_CSV_ROWS` | A claimed control needs a test |

## Checklist (each item has an acceptance test)

- [x] C1 Multi-registry robustness: 540 registries (3 sizes × 3 adoption profiles × 60 seeds); report flip rate, spread quantiles and by-profile results; show on the home page. Test: committed results equal a fresh run.
- [x] C2 Calibration: band cut-off grid, 1,000 random weightings, leave-one-check-out, per-check pass rates. Test: committed results equal a fresh run; bounds hold.
- [x] C3 Agreement tool with a fixed matching rule and bootstrap intervals. Test: committed results equal a fresh run; statistics helpers have known-value tests.
- [x] C4 Variance decomposition by definition axis. Test: shares are in [0,1] and sum to at most 1.
- [x] C5 `data/config/definition_axes.json` with a rationale per level. Test: config keys equal the code's literals.
- [x] C6 Consistency of structured fields with a plain reading of the wording, with kappa and intervals. Test: part of the calibration comparison.
- [x] C7 `CITATION.cff` and a tag-driven release workflow that attaches the offline file. Test: files parse; workflow runs on the next tag (not testable here).
- [x] C8 CSV size cap test. Test: truncation flagged and rows capped.
- [x] All results on a new Assurance page (EN/AR) with the limits stated beside them. Test: browser smoke and axe tests include the page.
- [ ] A human-labelled gold set for extraction accuracy. Not done: needs a person other than the author and was not available. The agreement figures are consistency checks, and the page says so.
- [ ] Practitioner review of the axes and the maturity ladder. Not done, same reason.

## What the new analyses found (reported as found, not as hoped)
- The "same target, different answer" finding depends on the population. The verdict flips in 80% of generated registries overall, in 100% where adoption is mid or high, and in 40% where adoption is low, because nothing reaches 50% under any definition there. The front page now says this instead of quoting one range.
- Which choice matters most: the maturity threshold explains about 53% of the variance, guardrails about 20%, the unit about 6%, the scope under 1%. The earlier framing that "the unit counted" is the main lever was not supported by this generator.
- The score has a floor effect: 8% of commitments name a way to measure them and 4% define all their terms. Those two checks barely change the ranking (rank correlation 0.999 and 1.0 when dropped). The checks still matter because the gap is the finding, but they do not separate commitments from one another.
- Band cut-offs are fragile at the edges: moving them by up to 10 points changes the band of up to 9 of 25 commitments. The ledger therefore shows the six marks, not only the band.
- A plain-text reading agrees with the structured fields on 16 of 18 numeric targets and 22 of 25 deadlines; kappa intervals are wide (0 to 1 and 0.44 to 1). Disagreements: C01, C10, C14, C24 (to be reviewed by a person).
- A blind second pass found 22 of 25 commitments (88%, 95% interval 72% to 100%). Missed: C06, C09, C16.

## Outcome (v1.3.0)
Evidence: 46 Python tests, 22 unit tests, 59 browser tests including the new page in EN/AR light/dark, 0 serious axe findings. Two items remain open and are labelled above (human gold set, practitioner review).
