# Risk register

Likelihood and impact: L (low), M (medium), H (high). Owner is a role, not a person.

| ID | Risk | Likelihood | Impact | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|
| R1 | A status is read as a verdict on an entity | M | H | Maintainer | Neutral wording, search log, "how to read this" text, band names describe wording | Any complaint, or a reviewer reads a status as blame |
| R2 | An extraction note misstates a source | M | H | Maintainer | Anchors, hashes, `verify-live`, human spot-check, corrections process | `verify-live` failure or a correction |
| R3 | A source page changes or disappears | H | M | Maintainer | Weekly drift workflow, `diff` command, retrieval dates | Drift workflow fails |
| R4 | Source terms do not allow what is stored | L | H | Sponsor | Store notes, hashes and short anchors only; takedown path | Legal objection |
| R5 | The headline synthetic spread is quoted as a real result | M | H | Maintainer | Violet label, banner, Assurance page, "depends on adoption level" | Any external quote without the label |
| R6 | A user's CSV contains personal data | L | H | Office analyst | Registry fields contain no personal data by design; processed in the browser only; CSP blocks outbound requests | A column that looks personal in a data-quality report |
| R7 | Dependency compromise | L | H | Maintainer | Pinned versions, lock file, audit, SBOM | Audit finding |
| R8 | Single maintainer | H | M | Sponsor | `CONTRIBUTING.md`, tests as documentation, `make reproduce` | Maintainer unavailable for two weeks |
| R9 | Arabic text is wrong or stiff | M | M | Reviewer | Native-speaker review before external use; parity test | Reviewer comment |
| R10 | Entities refuse to engage | M | M | Sponsor | Start with volunteers; questions are specific and short; no league table in the pilot | Fewer than 2 volunteers by week 2 |
| R11 | Score checks are read as a standard | M | M | Maintainer | Assurance page states floor effect and edge fragility; axes marked as proposals | A request to "certify" |
| R12 | Scope creep into performance scoring | M | H | Sponsor | Written non-goal in `docs/PILOT.md` and the README | Any request to rank entities by performance |
