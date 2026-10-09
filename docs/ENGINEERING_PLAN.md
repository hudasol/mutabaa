# Engineering plan: limitations, root causes, and how they get fixed

Written 2026-10-10 against v1.0.0. Every limitation has a root cause, a fix, and a round in which the fix lands. The rounds are four review passes, each from the point of view of an engineer at a different organisation. Those critiques are informed simulations from public information, not those organisations' views.

## 1. Limitations register

| ID | Limitation | Root cause | Consequence if left | Fix | Round |
|---|---|---|---|---|---|
| P1 | Quotes are checked against extraction notes, not against the live pages | The fetch tool returns model summaries, never page text. The build environment has no raw HTTP. Storing page text is not allowed. | A note can drift from the page, or be wrong, and every check still passes | Figure-token live verifier (`verify-live`): each source lists the figures that must appear on the page; it runs on a machine with real network (CI, a laptop) and fails on a missing figure | 1 |
| P2 | Source metadata errors (two sources had dates that the page shows) | Metadata was read from a summary that omitted bylines | Wrong ages, wrong ordering on clocks | Date and byline are verified by `verify-live`; a metadata completeness check in the validator | 1 |
| P3 | Evidence is thin: 10 items for 25 commitments | Partly real (official progress reports are rare, which is a finding), partly limited search breadth | "No public evidence" is read as "we did not look" | A search log per commitment, so the status means "searched these places on this date, found nothing"; two more official sources added; unfetched leads listed | 1 |
| P4 | Snapshot only; no history or change detection | Static design; one hand-edited JSON set | A target quietly changes and nobody sees it | Dated snapshots, a diff command, and a scheduled drift workflow | 1, 2 |
| P5 | Second extraction was one small model and 24 items | No gold-labelled set; comparison was done by hand | Agreement numbers cannot be trusted or repeated | A gold benchmark, an agreement tool with bootstrap confidence intervals, error taxonomy | 3 |
| M1 | Score checks have equal weight, are binary, and `measurement_source` fails almost always | The score was designed top-down and never calibrated | Floor effect: bands barely separate commitments; looks arbitrary to a sceptic | Written decision rules per check, weight-robustness analysis, a second-rater test, disclosure of the floor effect | 3 |
| M2 | The "0% to 88%" headline is one seed and one set of generator assumptions | Single synthetic registry | The headline could be an artefact of the generator | Multi-seed, multi-scenario robustness; variance decomposition of the share by definition axis | 3 |
| M3 | Definition axes and the maturity ladder are our proposals, unvalidated | No practitioner input available | Looks like we invented the vocabulary | Axes defined in a config file with rationale; mapping to published frameworks; consultation questions for the office | 2, 4 |
| M4 | No notion of stale evidence | Status ignores `as_of` age | A 2025 figure and a 2026 figure look equally fresh | Evidence age shown and a staleness flag | 1 |
| U1 | No saved work, no review workflow, no shareable state | Deliberately static for privacy; nothing persists | Cannot be used by a team; every session starts empty | Permalinks, a local workspace, signed export bundles, reviewer sign-off; a documented server tier for later | 1, 4 |
| U2 | Single registry; no view across entities | The data model and the page were built for one population | An office oversees many entities | Portfolio view with per-entity comparison | 4 |
| U3 | CSV upload has no column mapping and no data-quality report | First version assumed a fixed template | Real inventories never match a template | Column mapper, quality report, row-level fixes | 1 |
| U4 | Arabic is unreviewed; nothing checks that every English string has an Arabic one | Strings were written in one pass; no parity test | Missing or stale Arabic ships silently | Key-parity test, glossary, a review flag in the UI | 1, 4 |
| U5 | UI is clean but plain; accessibility not audited | No audit tooling in the loop | Fails an accessibility review; reads as a template | Design pass each round; automated axe audit in CI | all |
| E1 | The page loads fonts from Google | Default choice | A government network may block it; it leaks that the page was opened | Self-host fonts; zero third-party requests | 2 |
| E2 | No security headers, threat model, SBOM or pinned dependencies | Not in scope for v1 | Cannot pass a security review | CSP and headers, STRIDE threat model, SBOM, pinned and locked dependencies, dependency audit | 2 |
| E3 | No end-to-end tests; no requirement-to-test traceability | Unit tests only | A UI regression ships unnoticed | Playwright smoke and accessibility tests; a traceability matrix | 2 |
| E4 | Tags cannot be pushed from the build environment; releases are manual | Environment policy | No tagged history on the remote | Tag-driven release workflow; `CITATION.cff` | 3 |
| E5 | Python dependencies are ranges, no lock, no container | Early scaffold | Results differ across machines | Lock file, Dockerfile, one `make reproduce` | 2 |
| S1 | No adoption path, impact measures, or compliance mapping | Product was built before the buyer was modelled | Cannot be pitched as a product | Pilot KPIs, risk register, control mapping to UAE data-protection and AI instruments, buyer and rollout plan | 4 |
| S2 | Source reuse terms not documented | Not considered | A legal reviewer stops the project | Sources policy: what is stored, why it is allowed, how to take something down | 4 |

## 2. Why these gaps and regressions happen

1. **Tooling limits become data limits.** The fetch tool summarises, so notes are second-hand. The fix is not better notes, it is a check that does not depend on them: figure tokens verified against raw pages by a machine that can fetch them.
2. **Manual curation is error-prone and nothing watches it.** Dates were wrong because a human-like process copied them from a summary. Every field that can be checked mechanically (dates, hashes, anchors, figures, links) gets a check.
3. **Single-run claims.** The headline came from one seed. Any number shown on the front page must come with its spread.
4. **Design from the top down.** The score and the ladder were designed from first principles and never exercised against a second reader. Calibrate against an independent rater and publish the disagreement.
5. **Static is a trade-off, not a virtue.** Privacy and deployability are real wins, but they cost persistence and collaboration. Say so, and design the server tier so the static core is its client, not a rewrite.
6. **Regression guards.** Golden files for the engines, tamper tests for provenance, a generated-payload freshness test, and now live verification, drift monitoring and end-to-end tests. A change that breaks any of them fails CI.

## 3. Work method for each round

1. Critique the current product as that engineer would, in writing, with severity and evidence (`docs/reviews/NN-*.md`).
2. Turn the critique into a checklist. Every item has an acceptance test.
3. Implement. Tests first for engine changes.
4. Run the full suite, screenshot the UI, run the accessibility audit.
5. Commit, update `CHANGELOG.md` and the milestone list, push.
6. Re-read the checklist. Anything not done stays open in the file, labelled as such. Nothing is ticked without evidence.

## 4. Round themes

| Round | Lens | Theme | Version |
|---|---|---|---|
| 1 | ADEO analyst-engineer | Is it trustworthy enough to put in front of a supervisor, and usable daily? Provenance, freshness, workflow | v1.1.0 |
| 2 | EDGE engineer | Can it be deployed where the network is closed, and survive a security review? Offline, supply chain, assurance | v1.2.0 |
| 3 | TII researcher | Are the claims true, measured and repeatable? Benchmarks, statistics, robustness | v1.3.0 |
| 4 | ATRC programme engineer | Is there a path from prototype to a funded, governed product? Portfolio, compliance, pilot, roadmap | v1.4.0 |

See `docs/ARCHITECTURE.md` for the system design.
