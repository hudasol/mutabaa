# Changelog

Milestones are listed with their tag. Tags up to v1.4.0 were first created locally with `scripts/tag-milestones.sh` (it maps each tag to its commit SHA) and later pushed; v1.5.0 and v1.6.0 were tagged directly.

## v1.6.0: a command line, baselines and engineering gates
- Command line: `mutabaa score`, `questions` and `template` read a CSV or JSON commitments file (comma, semicolon or tab, quoted line breaks, UTF-8 or UTF-16), print text, JSON or CSV and set an exit code with `--strict` and `--min-ratio`; the repository commands moved to argparse; `docs/CLI.md`, `docs/USER_GUIDE.md`
- One reader in two languages: `pipeline/own.py` and the browser reader follow the same rules, held together by `data/golden/own_inputs.json` and `own_outputs.json` (awkward cases found by an independent review); deadlines accept dates, months, quarters and years and must be real dates
- Baselines: preregistered E5 (rule based extractors against the ledger and the blind second reading, with an exploratory random comparison) and E6 (status invariants and five mutants the checks must catch); 18 of 22 predictions hit, 4 missed and reported; shown on the Assurance page
- Engineering gates: mypy, ESLint, a bundle budget (`npm run check:bundle`), a 200,000 row speed guard, `scripts/benchmark.py`, dependabot, editorconfig, `docs/PERFORMANCE.md`
- Site: pages load on demand (first script 96 kB gzip), the offline file keeps a single script, My commitments draws at most 500 rows, UTF-16 and tab files are read, singular counts are correct
- Documents: product plan moved into `docs/`, README with screenshots, `python -m pipeline sync-docs` rewrites stale fact markers
- Open: native speaker review of Arabic and notes, legal read of the sources policy, a real pilot, a built Docker image, Arabic reader error messages

## v1.5.0: verifiability of the project itself
- Voice and identity: review documents renamed to role lenses with a no affiliation note; real entities named only in `docs/CONTEXT.md`; no em dashes; a voice test with its rules in `tests/voice_rules.json`
- Documents agree with code: `python -m pipeline facts` writes `results/facts.json`; numbers in documents are marked and checked by `tests/test_docs_agree.py`; `docs/EVALUATION.md` is rendered from results
- Contracts: a Python layer import test, JSON Schema files generated from the models with a staleness test and a TypeScript field check, a 90 percent coverage gate on `pipeline/`
- Decision records in `docs/adr/`, `docs/DATA_STATEMENT.md`, `docs/DECISIONS.md`
- Preregistered evaluation (`PREREGISTRATION.md`, `python -m pipeline evaluate`): four experiments, each prediction marked HIT or MISS; a second synthetic generator; Portfolio and Assurance text changed where the results required it
- My commitments page: an office scores its own commitments in the browser, with questions in English and Arabic; TypeScript score and questions held to Python by golden files
- Independent review acted on: disclaimer footer on phones and in print, print colours under the dark theme, the live verifier reads robots.txt, Python 3.12 floor, a portfolio golden file, synthetic label tests on every page, translated interface labels, an error boundary; rejected findings are listed in `docs/DECISIONS.md`
- Fixes: content hashes no longer depend on checkout line endings; `pipeline diff` now reports target changes and reads Arabic on Windows; the strip chart has a table alternative; synthetic entity names follow the reader's language

## v1.4.0: programme office lens review round
- Portfolio page: per entity share under six definitions, rank under each and rank range
- Uploaded CSV now kept across pages
- Pilot plan, risk register (checked by script), sources policy, corrections process with issue template, compliance mapping, roadmap with decision points, team-service design (not built), CONTRIBUTING and PR template

## v1.3.0: research institute lens review round
- `python -m pipeline analyse`: 540-registry robustness study, score calibration (band cut offs, random weights, leave one out), agreement with the blind second pass (bootstrap intervals), consistency check of fields against wording
- New Assurance page (EN/AR); home page now states that the verdict flip depends on adoption level
- Findings reported as found: maturity threshold drives most of the spread; two score checks are almost never passed; band edges are fragile
- Definition axes config with rationale, CITATION.cff, tag driven release workflow, CSV cap test

## v1.2.0: defence technology lens review round
- Self-hosted fonts, strict CSP (meta and headers), zero third party requests (tested)
- Single-file offline build with hash-pinned CSP; opens from file://
- Playwright smoke and axe accessibility tests (EN/AR, light/dark); contrast and table-role fixes
- docs/SECURITY.md (STRIDE), traceability matrix and checker, SBOMs, lock file, Dockerfile, `make reproduce`
- `python -m pipeline diff REF`; CSV export neutralises formula injection; dev dependencies upgraded (0 audit findings)

## v1.1.0: executive office lens review round
- Live verifier (`verify-live`), search log and coverage, evidence staleness, data-as-of and payload hash
- Home page leads with a tile map of the 25 real commitments; synthetic illustration moved second
- Neutral band names; questions for the entity (EN/AR); shareable URL state; CSV column mapper and quality report; sortable and groupable ledger; EN/AR parity test; weekly drift workflow

## v1.0.0: evaluation and documentation
- Blind second extraction (`docs/EVALUATION.md`): found one target the first pass missed (C25), added
- METHODOLOGY, REVIEW_CHECKLIST, PROPOSAL; README run instructions and status

## v0.7.0: workbench complete
- Pages: overview, ledger with evidence detail, clocks, Definition Lab (with client side CSV upload), maturity and guardrails, printable brief, method
- English and Arabic (right to left); synthetic and user-file data carry persistent banners
- CSV and JSON export of the ledger; vitest parity test against the Python golden file; CI site job

## v0.4.0: synthetic registry and sensitivity engine
- Seeded generator for a labelled synthetic registry (16 entities, ~570 items); `is_synthetic` is enforced by the schema
- 72-definition sensitivity sweep (unit x scope x threshold x guardrails) with a golden file for the TypeScript engine
- `data/synthetic/DATASHEET.md`

## v0.3.0: scoring and status engines
- `pipeline/score.py`: six check verifiability score; checks that do not apply are excluded, not failed
- `pipeline/status.py`: deterministic status; neutral default; media-only evidence never moves a status; unit mismatches flagged, never converted
- 14 tests on real data behaviour, including tamper tests (stale hash, bad anchor, media marked official)

## v0.2.0: real ledger and validation
- 12 sources (5 official statements, 3 official self-reports, 4 media) with extraction notes and SHA-256 hashes
- 24 commitments (federal, Abu Dhabi, national), 9 evidence items, 5 media reported claims held apart from status
- `python -m pipeline validate | rehash | build`; anchors must appear in the stored notes

## v0.1.0: scaffold
- Python package, typed schemas (real records, derived results, synthetic registry, definitions)
- Ruff + pytest configuration, CI workflow
- `docs/LIMITATIONS.md`

## v0.0.1-plan
- `plan.md`, README, MIT license, `.gitignore`
