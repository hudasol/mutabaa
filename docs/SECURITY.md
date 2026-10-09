# Security and threat model

Scope: the static site (Profiles A and B in `docs/ARCHITECTURE.md`) and the Python pipeline. Profile C (a team service) is design only and is not covered here.

## Assets
1. Integrity of the published numbers and their provenance (the main asset).
2. Availability of the page to a reader.
3. Confidentiality of a user's own CSV (it never leaves the browser).

## Trust boundaries
- Public web pages are untrusted input to a human curator, never executed. Only hashes, short anchors and notes are stored.
- A user-supplied CSV is untrusted input to the browser engine. It is parsed locally, rendered as text by React, and never sent anywhere.
- The build machine is trusted. The hosting platform is trusted to serve files, nothing more.

## Network behaviour
- The site makes **zero** third-party requests: fonts are bundled, there is no analytics, no API call, no service worker. A browser test fails if any request leaves the origin.
- `python -m pipeline verify-live` is the only code that uses the network. It sends plain GET requests to the URLs listed in `data/real/sources.json`, with an honest User-Agent, TLS verification on, retries with back-off, and no attempt to get around a refusal (a 403 is reported as *unreachable*). It sends no credentials and no data from the repository.

## Controls
| Control | Where |
|---|---|
| Content-Security-Policy: no inline script, no remote origins, `default-src 'none'` | `site/index.html`, `site/vercel.json`, `site/headers.example.txt` |
| Offline build pins its single inline script and style by SHA-256 | `site/vite.single.config.ts` |
| `nosniff`, `no-referrer`, restrictive Permissions-Policy, COOP, HSTS, `frame-ancestors 'none'` | `site/vercel.json` |
| Exact-pinned npm dependencies with a lock file; `npm audit` clean at release | `site/package.json` |
| Pinned Python versions | `requirements.lock` |
| SBOMs (CycloneDX) | `sbom/` |
| Tamper test: a changed extraction note fails validation | `tests/test_real_data.py` |
| Payload freshness test: committed JSON equals a rebuild | `tests/test_real_data.py` |

## STRIDE
| ID | Threat | Mitigation | Status |
|---|---|---|---|
| T1 | Spoofing: a look-alike site passes as Mutabaa or as an official product | Footer and README state it is a prototype, not an official product; no government branding is used | Mitigated |
| T2 | Tampering: an extraction note or source record is edited without the hash changing | SHA-256 per note, validator, tamper test | Mitigated |
| T3 | Tampering: a source page changes after extraction | Weekly `verify-live`; `diff` command shows changes | Mitigated (detects, does not prevent) |
| T4 | Tampering: a malicious CSV contains markup or formulas | Rendered as text by React; exports quote fields; CSV formula-injection prefixes are neutralised on export | Mitigated |
| T5 | Repudiation: no record of who changed data | Git history; commit attribution; data-as-of and payload hash shown in the UI | Mitigated for the repository |
| T6 | Information disclosure: the page tells a third party it was opened | No third-party requests; `no-referrer` | Mitigated |
| T7 | Information disclosure: user CSV leaves the browser | No network code path for uploads; CSP `connect-src 'self'` | Mitigated |
| T8 | Denial of service: a huge CSV freezes the tab | File-size cap and row cap with a visible message | See residual risks |
| T9 | Elevation of privilege: dependency compromise | Pinned and locked versions, audit, SBOM, no runtime dependencies beyond React | Accepted risk (supply chain cannot be reduced to zero) |
| T10 | Misleading output: a reader treats "no public evidence" as a failure | Neutral wording, search log, explicit "how to read this" text | Mitigated by design, reviewed by people in later rounds |

## Residual risks
- T8: confirm the CSV caps in the UI and add a test (tracked in `docs/reviews/03-tii.md` if not done in this round).
- Human review of the extraction notes and the Arabic text has not happened.
- The page relies on the host to send the headers; the meta CSP is the fallback and cannot set `frame-ancestors`.

## Reporting
Open a private security advisory on the GitHub repository.
