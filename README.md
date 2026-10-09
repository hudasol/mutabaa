# Mutabaa · متابعة

**A verifiability workbench for UAE government AI-transformation targets.**

*Mutabaa* (متابعة) is Arabic for "follow-up" or "monitoring".

The UAE has committed to moving 50% of federal government sectors, services and operations to agentic AI within two years. Abu Dhabi is targeting a fully AI-native government by 2027. Leaders will be assessed on progress. But "agentic", "service" and "50%" do not yet have published operational definitions, and public progress claims are not graded by evidence quality.

Mutabaa makes these targets **checkable**:

- **Ledger** of official commitments with a six-point *verifiability score* that names exactly what each target is missing (metric, baseline, target value, date-precise deadline, owner, measurement source).
- **Evidence timeline** where every progress claim is graded by source type, with a deterministic, neutral-by-default **status** ("no public evidence" never means "not done").
- **Definition Lab**: recomputes a headline "% agentic" under every defensible definition (unit of count × maturity threshold × guardrails × scope) so a policy team can see how much the number depends on the definition, before it is locked in.
- **Maturity ladder + self-assessment** (a *proposal*, not an official standard) with governance flags aligned to the National AI Strategy's governance objective.
- **Brief**: print-ready one-page summary.

Built from the point of view of an analyst in a government supervisory office, such as the Abu Dhabi Executive Office, whose job is to monitor implementation of strategic plans.

> **Status:** in active development. See [`plan.md`](plan.md) for the full plan and milestone tags, and the table below for what exists today.

## Data: what is real, what is synthetic

| Data | Type | Notes |
|---|---|---|
| Commitments, milestones, evidence | **Real, public** | Official sources first; secondary media graded lower and flagged |
| Service / operation registry | **Synthetic** | Generic archetypes, never real entity names; every record `is_synthetic: true`; always badged in the UI |
| Uploaded CSV | **Your data** | Processed in the browser only; never sent anywhere |

Real and synthetic numbers are never combined into one figure. The Definition Lab's claim is about *structure* (definition choice changes the headline), **not** about where any real entity sits.

## Project status

| Component | Status |
|---|---|
| Plan, README, license | ✅ |
| Schemas, tooling, CI | planned `v0.1.0` |
| Real ledger + validation | planned `v0.2.0` |
| Scoring + status engine | planned `v0.3.0` |
| Synthetic registry + sensitivity engine | planned `v0.4.0` |
| Site: overview, ledger, clocks | planned `v0.5.0` |
| Definition Lab, CSV upload, self-assessment | planned `v0.6.0` |
| Arabic / RTL, governance flags, brief | planned `v0.7.0` |
| Deploy + evaluation report | planned `v1.0.0` |

## Repository layout (target)

```
data/        real/ · synthetic/ · golden/ · gold/
pipeline/    Python reference implementation (schemas, validate, score, status, synth, sensitivity)
site/        Vite + React + TypeScript, English and Arabic (RTL)
docs/        METHODOLOGY · DATASHEET · RUBRIC · LIMITATIONS · REVIEW_CHECKLIST
tests/       pytest (Python) and vitest (TypeScript), with Python↔TypeScript parity on a golden file
```

## Principles

1. **Neutral by default.** Every commitment starts at "no public evidence".
2. **Grounded.** Every real field links to a source; numbers are machine-checked against the stored extract.
3. **Deterministic.** No model judgement at runtime; statuses and scores follow written rules.
4. **Honest about limits.** Synthetic data is labelled; the rubric is labelled a proposal; secondary sources are graded.

## Licence

Code: MIT. Dataset (`data/real`, `data/synthetic`): CC BY 4.0. Source material remains the property of its publishers; this repository stores URLs, retrieval dates and short anchors, not republished text.

## Author

Huda Mueen. Built as an independent project on UAE government AI-transformation targets.
