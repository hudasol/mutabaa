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

> **Status:** working prototype. Read [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) first. See [`plan.md`](plan.md) for the plan and [`docs/PROPOSAL.md`](docs/PROPOSAL.md) for the pilot path.

## Data: what is real, what is synthetic

| Data | Type | Notes |
|---|---|---|
| Commitments, milestones, evidence | **Real, public** | Official sources first; secondary media graded lower and flagged |
| Service / operation registry | **Synthetic** | Generic archetypes, never real entity names; every record `is_synthetic: true`; always badged in the UI |
| Uploaded CSV | **Your data** | Processed in the browser only; never sent anywhere |

Real and synthetic numbers are never combined into one figure. The Definition Lab's claim is about *structure* (definition choice changes the headline), **not** about where any real entity sits.

## Project status

| Component | Status | Tag |
|---|---|---|
| Plan, README, license | done | `v0.0.1-plan` |
| Schemas, tooling, CI | done | `v0.1.0` |
| Real ledger (12 sources, 25 commitments, evidence, claims) + validation | done | `v0.2.0` |
| Scoring and status engines | done | `v0.3.0` |
| Synthetic registry + 72-definition sensitivity engine | done | `v0.4.0` |
| Web workbench: ledger, clocks, Definition Lab with CSV upload, maturity and guardrails, brief | done | `v0.5.0` to `v0.7.0` |
| English / Arabic (RTL) | done, Arabic not yet expert-reviewed | `v0.7.0` |
| Evaluation (blind second extraction) | done, see [`docs/EVALUATION.md`](docs/EVALUATION.md) | `v1.0.0` |
| Live verifier, search log, offline build, security and e2e tests | done | `v1.1.0`, `v1.2.0` |
| Robustness, calibration, agreement, Assurance page | done | `v1.3.0` |
| Portfolio view, pilot plan, risks, sources policy, corrections, compliance mapping, roadmap | done | `v1.4.0` |
| Human review of extraction notes | open, see [`docs/REVIEW_CHECKLIST.md`](docs/REVIEW_CHECKLIST.md) | |

Tags are created locally with `scripts/tag-milestones.sh` because the build environment could not push tags.

## Run it

```bash
pip install -e ".[dev]"
python -m pipeline validate      # integrity checks on the real data
python -m pipeline build         # regenerate site/src/data/real.json
pytest && ruff check .

cd site && npm install && npm test && npm run dev
```

## Repository layout

```
data/real/        sources, commitments, evidence, claims, extraction notes (hashed)
data/synthetic/   labelled synthetic registry + DATASHEET.md
data/golden/      72-definition results that the Python and TypeScript engines must both match
pipeline/         Python reference: schemas, validate, score, status, synth, sensitivity
site/             Vite + React + TypeScript app (English / Arabic)
docs/             METHODOLOGY, EVALUATION, LIMITATIONS, REVIEW_CHECKLIST, PROPOSAL
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


## Offline and verification
- `cd site && npm run build:offline` writes `dist-offline/index.html`, one file that opens from a USB stick.
- `make reproduce` runs the whole check (needs Python, Node, git).
- `python -m pipeline verify-live` re-checks source pages (needs network); `python -m pipeline diff HEAD~1` shows what changed.
- Security notes: `docs/SECURITY.md`. Claim-to-test map: `docs/TRACEABILITY.md`.
- `python -m pipeline analyse` recomputes the robustness, calibration and agreement results shown on the Assurance page.
