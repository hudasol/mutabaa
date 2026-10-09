# Limitations

Mutabaa is a method demonstration built on public information. Read this before relying on any output.

## What this is not

- **Not a measurement of any real entity.** Real entity-level service inventories are not public. The registry used by the Definition Lab is **synthetic** (generic archetype entities, a seeded generator, documented in `DATASHEET.md`). Findings from it are about *structure* (how much a headline percentage depends on its definition), not about where any real entity sits.
- **Not an assessment of government performance.** A status of `no-public-evidence` means "nothing public was found that maps to this target", not "not done". Internal tracking (for example, by a supervisory office) will know more than public sources do.
- **Not an official standard.** The L0–L4 maturity ladder and the verifiability checks are proposals made for this project.

## How the real data was collected

- Sources were collected on **2026-10-09** through a web-fetch tool that returns a model-generated extraction of each page, not the raw page. The repository stores **extraction notes** (`data/real/extracts/`) written during collection, and a SHA-256 hash of each notes file.
- The validator checks that every anchor phrase and every number in a record appears in the **extraction notes** for its source. It does **not** re-fetch the live page. A reviewer should open the source URL and check the record. `REVIEW_CHECKLIST.md` lists the items worth checking first.
- Some pages could not be retrieved (a government news-agency page returned no body text; one news page required a manual permission that was not available). Those pages are not used.
- Some figures circulate in secondary reporting but were **not found in the official statement checked** (for example a "150 million data points a month" figure for a federal performance system, and a "38 entities" figure). They are kept in the claim register with the corroboration label `not-in-official-statement` and are excluded from status computation.
- One secondary source states it was produced with AI assistance. It is flagged `ai_assisted`.
- **No third-party (independent) corroboration** of any progress claim was found in the sources reviewed. Every progress figure in the ledger is either an official self-report or secondary reporting. This is a finding about the sources reviewed, not proof that none exists.

## Extraction quality

- Extraction was done by a language model. Quality is reported in `docs/EVALUATION.md` as agreement between two independent extraction passes and against a hand-checked set. That is **inter-extractor agreement, not independent human validation.** Treat it as an upper-bound sanity check.
- Arabic text in the product was written by a language model and has not been reviewed by a native-speaking domain expert. Review before any external use.

## Definition Lab

- The Definition Lab enumerates 72 definitions (4 units × 3 scopes × 3 maturity thresholds × 2 guardrail settings). These are defensible readings of "50% of sectors, services and operations", not an exhaustive or official list.
- Rules for how an *entity* or *sector* counts as transformed (a majority of its in-scope items qualify) are choices made here; other rules are possible and would move the numbers.
- Results on the synthetic estate depend on the generator's assumptions (documented in the datasheet). Uploading your own registry (CSV, processed in the browser only) replaces those assumptions with your data.

## Scope

- Focused on AI-transformation targets (federal and Abu Dhabi). Other domains are out of scope for now.
- Static snapshot. Data updates are reviewed commits; there is no live scraping.
