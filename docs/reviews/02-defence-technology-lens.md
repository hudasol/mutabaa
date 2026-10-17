# Review 2: an AI engineer at a defence and advanced-technology group (EDGE lens)

Simulated critique, written from public information about how such organisations evaluate software, not from inside knowledge. Reviewed: v1.1.0.

## What I would say in the first five minutes
"The idea is fine and the data discipline is better than most. Now show me it runs on a closed network, makes no outside calls, can be built the same way twice, and has a list of what could go wrong. Today the page phones Google for fonts, there are no security headers, I can't open it from a USB stick, and nothing drives a real browser through it."

## Findings

| # | Severity | Finding | Evidence in v1.1.0 | Why it matters to me |
|---|---|---|---|---|
| B1 | High | The page makes third-party requests (Google Fonts) | `site/index.html` | Blocked on a closed network; leaks that the page was opened; breaks the "no network" claim |
| B2 | High | No Content-Security-Policy or other headers | No headers file | Cannot pass a basic web review |
| B3 | High | No threat model | Nothing in `docs/` | I need to see what was considered, including the CSV upload |
| B4 | High | Cannot run from a file or a USB stick | Module scripts and fonts need a server | The air-gapped profile (B) is claimed in the plan but not delivered |
| B5 | Medium | No software bill of materials; no dependency audit | Not generated | Procurement asks for it first |
| B6 | Medium | Python dependencies are ranges; no lock; no container | `pyproject.toml` | Results should be the same on any machine |
| B7 | Medium | No browser-level tests, no accessibility audit | Unit tests only | A UI regression or an accessibility failure ships unnoticed |
| B8 | Medium | No traceability from requirement to test | None | Assurance needs "which test covers this claim" |
| B9 | Medium | No way to see what changed between two data versions | Single snapshot | A quietly edited target should be visible |
| B10 | Low | Verifier network behaviour is undocumented | Code only | A reviewer needs to see exactly what leaves the machine, and when |

## Checklist (each item has an acceptance test)

- [x] B1 Self-host fonts; no external URL anywhere in the build. Test: script scans `dist` for http(s) origins; browser test records zero third-party requests.
- [x] B2 CSP and security headers shipped as `vercel.json` and a generic `_headers`; meta CSP in the page. Test: browser test loads with the policy and sees no violations.
- [x] B3 `docs/SECURITY.md`: assets, trust boundaries, STRIDE table, CSV upload, supply chain, residual risks. Test: file exists and every threat has a mitigation or an accepted-risk note (checked by a script).
- [x] B4 Single-file offline build that opens from `file://`. Test: browser test opens the file and sees the headline.
- [x] B5 SBOM (CycloneDX) for npm and Python; `npm audit` in CI. Test: generated and non-empty.
- [x] B6 Python lock file, Dockerfile, `make reproduce`. Test: reproduce target runs validate, tests, build and fails if the payload changes.
- [x] B7 Playwright smoke tests for every page, EN and AR, light and dark, plus axe. Test: zero serious or critical violations.
- [x] B8 Traceability matrix. Test: script fails if a listed test does not exist.
- [x] B9 `python -m pipeline diff REF` shows status and commitment changes against a git ref. Test: unit test with two payloads.
- [x] B10 Document network behaviour of `verify-live` in SECURITY.md. Test: stated in the file.

## Outcome (v1.2.0)
All items done. Evidence: 38 Python tests, 20 unit tests, 53 browser tests (0 serious or critical axe findings in EN/AR, light/dark; 0 third-party requests; offline file opens), `npm audit` reports 0 vulnerabilities, traceability check passes. Axe found real issues on the first run (low-contrast muted text, invalid table roles on the clocks page, opacity on excluded evidence); all fixed. Not done: Docker image was written but not built here (no Docker in this environment); `make reproduce` was not run end to end for the same reason, its steps were run individually.
