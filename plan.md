# Mutabaa (متابعة) — Product Plan

> Status: living document. Last updated 2026-10-09. Owner: Huda Mueen.

Mutabaa is a **verifiability workbench for government AI-transformation targets**. It turns headline commitments ("50% agentic", "100% digitised", "200+ AI solutions") into evidence-linked, checkable records, and shows how much the headline number depends on how its terms are defined.

It is designed from the point of view of an analyst inside a government supervisory office (the Abu Dhabi Executive Office, ADEO, is the reference user): someone whose job is to monitor the implementation of strategic plans and assess entity performance.

---

## 1. The problem

The UAE and Abu Dhabi have made AI-transformation commitments that senior officials will be judged on:

| Level | Commitment (as officially announced) | Clock |
|---|---|---|
| Federal | 50% of federal government sectors, services and operations on agentic AI within two years; ministers, directors-general and entity heads assessed on adoption | Announced 23 Apr 2026 → ~Apr 2028 |
| Abu Dhabi | World's first fully AI-native government across digital services; AED 13bn; 100% sovereign cloud; 100% of processes digitised and automated; 200+ AI solutions | Launched 21 Jan 2025 → "by 2027" |
| National | We the UAE 2031 (government performance pillar); National AI Strategy 2031 (eight objectives incl. governance) | 2031 |

These targets are hard to verify from the outside, and likely hard to compare across entities even from the inside, for definitional reasons that are visible in the public record alone:

1. **One percentage, three units.** The federal target is "50% of sectors, services *and* operations". A sector, a service and an operation are different denominators, and each produces a different percentage for the same estate.
2. **"Agentic" has no published operational definition.** Reporting from the August 2026 workshop says systems will be classified through a self-assessment mechanism, but no criteria or levels had been published at the time of writing.
3. **Vocabulary drift within one programme.** Abu Dhabi reports progress in "AI use cases" (100+ across 40+ entities, Sept 2025) against a target worded in "AI solutions" (200+), with "AI agents" (1,000+) as a third unit in 2026.
4. **Assessment criteria for leaders are qualitative.** The official Cabinet statement lists abilities and understanding, not measurable thresholds.
5. **Deadlines without dates.** "By 2027" does not say whether that is 1 January or 31 December.
6. **Progress claims mix grades of evidence.** Official self-reports, secondary media and third-party sources appear side by side. Some figures circulate in media but were not found in the official statement (e.g. "up to 70% faster lawmaking" is a projection, not a result).
7. **Training figures don't reconcile at a glance.** "95% of 30,000+ employees trained" (Sept 2025), "20,000 by end of 2026" and "~23,000 by early 2027" are different programmes or definitions; nothing public maps one to the other.

None of this is criticism. These are normal properties of announcements. But a supervisory body whose mandate is to monitor implementation needs targets that are *measurable*, and needs to know *which* are not yet, and *why*.

> **Problem statement.** The UAE has committed to AI-transformation targets that leaders will be assessed on, but the targets cannot yet be verified because "agentic", "service" and "50%" are not operationally defined, and public progress claims are not graded by evidence quality.

## 2. Who it is for

| Persona | Job to be done | What Mutabaa gives them |
|---|---|---|
| **Performance analyst** (ADEO-like) | Monitor strategic-plan implementation; brief leadership | Ledger of commitments with a verifiability score, evidence timeline, and rule-based status; one-page brief |
| **Policy designer** | Write targets that can be checked | Definition Lab: see how a headline % swings across definitions; Verifiability checklist for new targets |
| **Entity AI officer** | Self-assess services against a common ladder | Maturity self-assessment with governance flags; CSV import/export |
| **Auditor / reviewer** | Check provenance | Every field links to a source; methodology and limitations are in the product |

## 3. Product scope

### 3.1 Modules

1. **Ledger.** Commitments (targets, milestones, policies, assessments) with provenance. Each has a six-point verifiability score (metric, baseline, target value, deadline, owner, measurement source) and names exactly what is missing.
2. **Evidence timeline.** Dated progress claims linked to commitments, each graded: `official-self-report`, `official-statement`, `secondary-media`, `third-party`.
3. **Status engine.** Deterministic, rule-based. Default is "no public evidence". It never infers success and never infers failure.
4. **Clocks.** Timeline of federal vs Abu Dhabi deadlines and milestones; makes the "different jurisdictions, shared vocabulary" point visually.
5. **Definition Lab.** The key insight module. Given a registry of services/operations, recompute the headline "% agentic" under every defensible definition (unit of count × maturity threshold × guardrail requirement × scope). Shows the range, and which definitional choice moves the number most. Works on the built-in **synthetic** estate or on an **uploaded CSV** (processed in the browser; nothing leaves the device).
6. **Maturity ladder + self-assessment.** A proposed L0–L4 rubric (manual → digitised → automated → AI-assisted → agentic within guardrails) and a guided self-assessment. Clearly labelled *our proposal*, not an official standard.
7. **Governance flags.** For each AI deployment: declared human oversight, audit trail, UAE data residency, fallback path. Rolled up per entity, aligned to National AI Strategy objective 8 (governance and regulation).
8. **Brief.** Print-ready one-page executive summary generated from the data.
9. **Methodology, Datasheet, Limitations.** In-product, bilingual.

### 3.2 Non-goals

- No claim about the real state of any real entity's AI maturity. Real entity-level data is not public; the registry is synthetic and labelled everywhere.
- No scoring of individuals or of named real entities.
- No live scraping at runtime. Data updates are reviewed commits.
- Not a replacement for the federal Proactive Government Performance System or internal ADEO tooling. Mutabaa audits whether *targets* are measurable and lets a definition be stress-tested before it is locked in.

## 4. Data policy

| Data | Type | Rule |
|---|---|---|
| Commitments, milestones, evidence | **Real, public** | Official government sources first; secondary sources are graded lower and marked. Short anchors only; no republishing of source text. |
| Service/operation registry | **Synthetic** | Generic archetype entities (never real entity names), seeded generator, documented in `docs/DATASHEET.md`. Every record carries `is_synthetic: true`; the UI shows a persistent badge; real and synthetic figures are never combined into one number. |
| User-uploaded CSV | **User data** | Parsed client-side only; validated against the schema; never sent anywhere. |

Synthetic data is labelled unambiguously and documented (purpose, generation process, limits), following published guidance on documenting synthetic collections.

## 5. Methodology (summary; full text in `docs/METHODOLOGY.md`)

### 5.1 Verifiability score
Six binary checks per commitment: **metric**, **baseline**, **target value**, **deadline (date-precise)**, **owner (named entity)**, **measurement source declared**. Score = checks passed / 6. Bands: *Checkable* (6), *Partly checkable* (3–5), *Not yet checkable* (0–2). The record lists the missing checks.

### 5.2 Status rules
Statuses are defined up front (as government trackers such as Canada's mandate-letter tracker do) and every item starts neutral until evidence appears:

| Status | Rule |
|---|---|
| `not-checkable` | Verifiability < 3/6: cannot be tracked as written |
| `no-public-evidence` | Default for checkable items with no evidence attached |
| `activity-reported` | Evidence of activity (programme, rollout, training) but no quantity tied to the target |
| `milestone-reported` | A quantified progress figure that maps to the commitment's metric |
| `target-claimed-met` | Owner or official source states the target is met |

Each evidence item carries a **grade**. A status is annotated `self-reported` unless corroborated by a different-grade source.

### 5.3 Maturity ladder (proposal)
`L0` manual → `L1` digitised → `L2` rule-based automation → `L3` AI-assisted, human approves each action → `L4` agentic: acts within guardrails, humans handle exceptions. Governance flags are tracked independently of level.

### 5.4 Definition Lab
Axes: **unit** (services, transaction-weighted, entities, sectors), **scope** (services only; + business services; + internal operations), **threshold** (≥L2, ≥L3, ≥L4), **guardrails** (not required; oversight + audit + residency required). The engine enumerates every combination, reports min/median/max, and a one-at-a-time swing per axis. **The claim is about structure** (definition choice changes the headline), **not** about where any real entity sits.

## 6. Architecture

Static, no runtime backend, no API keys, nothing that can fail overnight.

```
mutabaa/
├─ data/
│  ├─ real/         commitments.json, evidence.json, sources.json, extracts/
│  ├─ synthetic/    registry.json  (is_synthetic: true)
│  ├─ golden/       sensitivity.golden.json  (Python ↔ TypeScript parity)
│  └─ gold/         hand-checked commitments for evaluation
├─ pipeline/        Python 3.11+: schemas, validate, score, status, synth, sensitivity, build
├─ tests/           pytest
├─ site/            Vite + React + TypeScript; EN/AR (RTL); engine mirrored in TS
└─ docs/            METHODOLOGY, DATASHEET, RUBRIC, LIMITATIONS, REVIEW_CHECKLIST
```

**Pipeline:** collect (official sources, stored as extracts + hash) → extract (structured JSON) → validate (schema; every number in a record must appear in its source extract) → score → status → synth → sensitivity → build site data.

**Dual implementation of the engine.** Python is the reference implementation; TypeScript runs in the browser (needed for CSV upload). A golden file produced by Python must match TypeScript output exactly, enforced by tests.

## 7. Source base (collected 2026-10-09)

Official sources are preferred; secondary sources are graded lower and flagged.

- UAE Cabinet / Media Office statement on the agentic AI framework (23 Apr 2026).
- Abu Dhabi Media Office and DGE: Digital Strategy 2025–2027 launch and updates; DGE 2025 highlights (8 Jan 2026); DGE–Microsoft Frontier Employee Programme (6 Jul 2026).
- Gulf News and other reporting on the Higher Committee for Agentic AI workshop (Aug 2026): five tracks, FedAI platform, self-assessment classification.
- UAE government portal: We the UAE 2031 indicators; National AI Strategy 2031 objectives and figures.
- UAE Cabinet: Regulatory Intelligence ecosystem (14 Apr 2025).
- AI-assisted trade articles are used only as secondary evidence and are marked `secondary-media`; figures that the official statement does not contain are flagged *unverified against official source*.

## 8. Quality bar

- Every real record has a source, retrieval date, and a short anchor; numbers are machine-checked against the stored extract.
- Deterministic status and scoring; no model judgement at runtime.
- Python ↔ TypeScript parity test on the golden file.
- Gold set evaluation reports precision, recall and hallucination rate **separately** by field type (identifiers exact; quantities with tolerance), as good practice in extraction benchmarking.
- CI runs lint, tests, validation, and a build.
- Accessibility: keyboard navigable, sufficient contrast, RTL tested.

## 9. Milestones and tags

| Tag | Content |
|---|---|
| `v0.0.1-plan` | `plan.md`, README, license |
| `v0.1.0` | Schemas, repo tooling, CI, docs skeleton |
| `v0.2.0` | Real ledger + evidence + validation |
| `v0.3.0` | Verifiability scoring + status engine + tests |
| `v0.4.0` | Synthetic registry + datasheet + sensitivity engine (Python) |
| `v0.5.0` | Site core: overview, ledger, clocks |
| `v0.6.0` | Definition Lab + CSV upload + maturity self-assessment (TypeScript engine, parity tests) |
| `v0.7.0` | Arabic/RTL, governance flags, brief, exports |
| `v1.0.0` | Deploy, gold-set evaluation report, final docs |

## 10. Path to a pilot with ADEO

1. **Show the method on public data** (this repo).
2. **Pilot swap-in.** Replace the synthetic registry with a real service/operation inventory via the documented CSV schema. No code change.
3. **Calibrate definitions with the supervisory team.** The Definition Lab output is a decision aid: which definition of "50%" to lock in.
4. **Deployment options.** Static bundle that can run inside a government network or sovereign cloud; no external calls; no data egress.
5. **Open questions for ADEO** (to learn, not assume): what is tracked today, in what system, and who owns the definitions.

## 11. Risks

| Risk | Mitigation |
|---|---|
| Reads as criticism of government | Framed as making targets checkable; neutral language; "no public evidence" never means "not done" |
| Secondary sources wrong or AI-assisted | Graded lower, flagged, never used alone for a status above `activity-reported` |
| Synthetic numbers mistaken for real | Persistent badge, separate namespace, datasheet, tests that fail if a synthetic record lacks the flag |
| Extractions from fetched extracts, not raw pages | Disclosed in `docs/LIMITATIONS.md`; reviewer checklist and URL list provided for independent checking |
| Rubric treated as official | Labelled "proposal" everywhere |
| Overbuilding | Walking skeleton first; each tag leaves a coherent product |

## 12. Reference points that shaped the design

- Government commitment trackers (e.g. Canada's Mandate Letter Tracker, Code for Africa's PromiseTracker): explicit status definitions, evidence-linked ratings, published methodology, neutral default.
- Structured-extraction benchmarks: grounding each value to its source is the weak point; score fields by type; separate omission from hallucination.
- Guidance on synthetic data: label it unambiguously, document how it was produced and its limits.
