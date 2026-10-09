# Compliance mapping (the author's reading, not legal advice)

Purpose: show which public frameworks a pilot should be checked against and where Mutabaa already helps. It does not claim compliance with any of them. Each row needs review by the organisation's own counsel or risk team.

| Framework (public) | What it asks, in short | Where Mutabaa stands | Gap |
|---|---|---|---|
| UAE Federal Decree-Law No. 45 of 2021 on Personal Data Protection | Lawful, limited processing of personal data | Registry fields contain no personal data; the CSV is processed in the browser only; no network path for uploads (CSP, tested) | A pilot must confirm its export has no personal data; counsel to confirm applicability |
| UAE Federal Decree-Law No. 38 of 2021 on Copyright and Neighbouring Rights | Rights in published works | Notes in own words, short anchors, no mirroring (`docs/SOURCES_POLICY.md`) | Counsel to confirm that short anchors and notes are acceptable |
| ISO/IEC 42001:2023 (AI management systems) | An organisation manages AI systems with defined roles, risks, monitoring | Mutabaa uses no AI at runtime. The pipeline is deterministic. A model was used only for the blind second reading, which is documented | If Profile C adds a model, a risk assessment and monitoring are needed first |
| NIST AI Risk Management Framework 1.0 | Govern, map, measure, manage AI risks | Risk register (`docs/RISKS.md`), measured claims (Assurance page), traceability matrix | Impact assessment with real stakeholders |
| OECD AI Principles | Transparency, accountability, robustness | Every status traces to a source; limits are shown beside results; corrections process | Independent review |
| WCAG 2.1 AA (accessibility) | Perceivable, operable, understandable, robust | Automated axe tests in EN/AR, light/dark, zero serious or critical findings | Manual screen-reader review; automated tests find only part of the issues |
| UAE and Abu Dhabi government AI policies and data standards | Entity-specific rules on AI use and data handling | Not mapped. Their texts were not reviewed for this project | Needed before any pilot with entity data |

Residual: this table is a starting point for a conversation with the reviewing body.
