# Review 4: a programme engineer at an applied-research and technology-programme body (ATRC lens)

Simulated critique, written from public information about how such bodies assess projects, not from inside knowledge. Reviewed: v1.3.0.

## What I would say in the first five minutes
"Technically credible now. My question is different: who uses it, what does a pilot cost and prove, what could go wrong, which rules apply, who is allowed to change the data, and what happens when an entity says you got it wrong? And my office oversees many entities, not one registry."

## Findings

| # | Severity | Finding | Evidence in v1.3.0 | Why it matters |
|---|---|---|---|---|
| D1 | High | No view across entities | Lab and Maturity show a pooled registry | The buyer's job is to compare entities fairly |
| D2 | High | No pilot plan with success measures | None | Funding is released against measurable outcomes |
| D3 | High | No risk register | Limits are listed, risks are not | A programme board asks for owners and mitigations |
| D4 | High | No policy for source reuse or takedown | Notes and hashes only | Legal review stops the project without it |
| D5 | High | No right-of-reply process | Nothing for an entity to say "this is wrong" | A tool that grades public commitments will be challenged |
| D6 | Medium | No mapping to the rules a deployment must respect | None | Needed before any pilot with real registry data |
| D7 | Medium | Contribution and data-change governance is undefined | Single author | Who may change a status or a source? |
| D8 | Medium | No service design for the team tier | Profile C is a diagram | Needs an API contract and an audit model before anyone builds it |
| D9 | Medium | Uploaded CSV is lost when moving between pages | Page-local state | A daily user loses work |
| D10 | Low | No roadmap with decision points | None | Funders want stages and exit criteria |

## Checklist (each item has an acceptance test)

- [x] D1 Portfolio page: per-entity share under six definitions, rank under each, rank range, EN/AR, works on a user's CSV. Test: unit tests on ranking and ties; browser and axe tests on the page.
- [x] D9 Working data set shared across pages. Test: browser test uploads a CSV on one page and sees it on another.
- [x] D2 `docs/PILOT.md`: scope, roles, 12-week plan, measures with targets, stop criteria. Test: file present; every measure has a target and a way to measure.
- [x] D3 `docs/RISKS.md`: register with likelihood, impact, owner role, mitigation, trigger. Test: script checks every row has all fields.
- [x] D4 `docs/SOURCES_POLICY.md`: what is stored and why, what is not, takedown path.
- [x] D5 `docs/CORRECTIONS.md` and an issue template for corrections; response times stated.
- [x] D6 `docs/COMPLIANCE.md`: mapping to named public frameworks, labelled as the author's reading and not legal advice.
- [x] D7 `CONTRIBUTING.md` with a data-change checklist, and a pull-request template.
- [x] D8 `docs/design/openapi.yaml` and `docs/design/SERVICE.md` for the team tier: roles, audit log, retention. Design only, labelled.
- [x] D10 `docs/ROADMAP.md` with stages, decision points and exit criteria; `docs/PROPOSAL.md` updated.
- [ ] A real pilot with a real entity registry. Not done and cannot be done from here. The pilot plan says what it would prove.
- [ ] Legal review of `docs/SOURCES_POLICY.md` and `docs/COMPLIANCE.md`. Not done.

## Outcome (v1.4.0)
Evidence: 46 Python tests, 25 unit tests, 66 browser tests (accessibility, offline, zero external requests, CSV workflow), traceability and risk checks pass. The Portfolio page found that on the synthetic registry the rank of many entities moves by several places depending on the definition, which is the argument against a single-definition league table. The first accessibility run failed on the new page (contrast on tinted cells, scrollable region not focusable); both fixed. Two items remain open and are labelled above.
