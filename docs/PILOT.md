# Pilot plan (proposal)

Status: proposal. Nothing here has been run with a real entity.

## Question the pilot answers
Can an office that oversees AI programmes use Mutabaa, on a registry it already holds, to (1) see which commitments it cannot currently verify, (2) see how much a headline percentage depends on its definition, and (3) send entities specific questions, with less effort than its current process?

## Scope
- 12 weeks. One overseeing office, 3 to 5 entities that volunteer, one registry export each (service or operation name, entity, sector, audience, annual transactions, maturity level, four guardrail flags).
- Profile B (static, offline) only. No data leaves the office's machines. No access to production systems.
- Mutabaa's public-source ledger is shown beside the pilot data but never merged with it.

## Roles
| Role | Does |
|---|---|
| Office sponsor | Chooses entities, owns the definition decision |
| Office analyst (2 people) | Loads exports, reviews outputs, logs corrections |
| Entity contact (per entity) | Confirms their export, answers questions |
| Maintainer | Fixes defects, keeps the data process in `CONTRIBUTING.md` |
| Reviewer (outside the project) | Samples 20% of outputs against sources |

## Plan
| Weeks | Work | Output |
|---|---|---|
| 1-2 | Agree columns and definitions; dry run on synthetic data | Column mapping per entity |
| 3-4 | Load real exports; data-quality report; fix at source | Clean registries |
| 5-8 | Portfolio and Definition Lab reviews with the sponsor; send questions to entities | Decision note on the definition |
| 9-10 | Reviewer samples outputs; defects fixed | Review log |
| 11-12 | Measure, write up, decide | Pilot report |

## Measures and targets
| Measure | Target | How measured |
|---|---|---|
| Rows loaded without manual repair | at least 90% | Data-quality report |
| Analyst time to produce the monthly briefing | at least 30% less than the office's own baseline | Timed before and after, same analyst |
| Reviewer disagreement with an output | under 5% of sampled outputs | Review log |
| Entities that answer at least one generated question | at least 3 of 5 | Correspondence log |
| Definition decision recorded by the sponsor | 1 | Decision note |
| Defects that change a status or a share | 0 open at week 12 | Issue tracker |
| Accessibility (axe, serious or critical) | 0 | CI |

## Stop criteria
Stop and report if: the office cannot supply exports within week 4; reviewer disagreement exceeds 15%; any data leaves the office's machines; the sponsor withdraws.

## What the pilot would not prove
Whether entities are performing well. Mutabaa does not measure performance.
