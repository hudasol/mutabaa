# Limitations

Mutabaa is a method demonstration built on public information. Read this before relying on any output.

## What this is not

- **Not a measurement of any real entity.** Real service inventories at entity level are not public. The registry used by the Definition Lab is **synthetic** (generic archetype entities, a seeded generator, documented in `DATA_STATEMENT.md`). Findings from it are about *structure* (how much a headline percentage depends on its definition), not about where any real entity sits.
- **Not an assessment of government performance.** A status of `no-public-evidence` means "nothing public was found that maps to this target", not "not done". Internal tracking (for example, by a supervisory office) will know more than public sources do.
- **Not an official standard.** The L0 to L4 maturity ladder and the verifiability checks are proposals made for this project.

## How the real data was collected

- Sources were collected on **2026-10-09** through a web fetch tool that returns a generated extraction of each page, not the raw page. The repository stores **extraction notes** (`data/real/extracts/`) written during collection, and a SHA-256 hash of each notes file.
- The validator checks that every anchor phrase and every number in a record appears in the **extraction notes** for its source. It does **not** refetch the live page. A reviewer should open the source URL and check the record. `REVIEW_CHECKLIST.md` lists the items worth checking first.
- Some pages could not be retrieved (a government news agency page returned no body text; one news page required a manual permission that was not available). Those pages are not used.
- Some figures circulate in secondary reporting but were **not found in the official statement checked** (for example a "150 million data points a month" figure for a federal performance system, and a "38 entities" figure). They are kept in the claim register with the corroboration label `not-in-official-statement` and are excluded from status computation.
- One secondary source states it was produced with AI assistance. It is flagged `ai_assisted`.
- **No independent (third party) corroboration** of any progress claim was found in the sources reviewed. Every progress figure in the ledger is either an official self-report or secondary reporting. This is a finding about the sources reviewed, not proof that none exists.

## Extraction quality

- Extraction was done by a language model. Quality is reported in `docs/EVALUATION.md` as agreement between two extraction passes over the same notes (the second pass found <!-- fact:agreement.recall.found -->93<!-- /fact --> of <!-- fact:agreement.recall.n -->96<!-- /fact --> ledger commitments). That is **agreement between extractors, not independent human validation.** Treat it as an upper bound sanity check.
- Arabic text in the product was written by a language model and has not been reviewed by a native speaker with domain knowledge. Review before any external use.

## Definition Lab

- The Definition Lab enumerates <!-- fact:sweep.definitions -->72<!-- /fact --> definitions (4 units, 3 scopes, 3 maturity thresholds and 2 guardrail settings). These are defensible readings of "50% of sectors, services and operations", not an exhaustive or official list.
- Rules for how an *entity* or *sector* counts as transformed (a majority of its in scope items qualify) are choices made here; other rules are possible and would move the numbers.
- Results on the synthetic estate depend on the generator's assumptions (documented in the datasheet). Uploading your own registry (CSV, processed in the browser only) replaces those assumptions with your data.

## Scope

- Focused on AI transformation targets (federal and Abu Dhabi). Other domains are out of scope for now.
- Static snapshot. Data updates are reviewed commits. A weekly workflow reads the source pages and reports a change in their text, but it edits no ledger record; a person decides what a change means.

## Validity, linter, card and monitoring (v1.8.0)

- **Validity (E8) is weak evidence.** The score separates commitments that later received a dated official report from those that did not with AUC <!-- fact:e8.auc -->0.69<!-- /fact -->, but the interval runs from <!-- fact:e8.ci_low -->0.52<!-- /fact --> to <!-- fact:e8.ci_high -->0.85<!-- /fact -->, and <!-- fact:e8.searches.not_run -->53<!-- /fact --> registered searches never ran. Where the full protocol was run the AUC is <!-- fact:e8.full.auc -->0.52<!-- /fact -->, which is chance. Most positives come from the press office of one government. The study does not show that a clearer wording causes a report, only that the two were associated in <!-- fact:e8.n -->36<!-- /fact --> commitments.
- **The linter reads wording only.** It recovers whether a number is present (F1 <!-- fact:e9.number.f1 -->0.91<!-- /fact -->) but not who owns a commitment (accuracy <!-- fact:e9.owner -->0.30<!-- /fact -->, below a constant baseline of <!-- fact:e9.owner.baseline -->0.74<!-- /fact -->), and it cannot recover a source. A result says what a sentence leaves open. It never says whether a commitment is met.
- **The Definition Card is a record, not an endorsement.** It checks that a definition is complete and recomputes a headline on a synthetic registry. It does not say which definition is right.
- **The weekly check detects changed text, not changed meaning.** A page that moves its content, adds a cookie banner or blocks automated requests can look like a change. Pages that were already unreachable raise no new issue.
- **Arabic is unreviewed.** The glossary and the review kit prepare the work; they do not replace a native reader.
