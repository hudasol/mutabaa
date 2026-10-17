# Data statement

This statement describes the data Mutabaa uses: a real public dataset in `data/real/`, a labelled synthetic registry in `data/synthetic/`, and files a user uploads in the browser. Mutabaa is a student prototype and a proposal seed, not a deployment. Nothing in the data, the scores or the statuses implies endorsement by any entity, and nothing here is an assessment of government performance. Read `docs/LIMITATIONS.md` alongside this statement.

Counts are not written here, because they change when the data changes. The current counts of sources, commitments, evidence items, claims, unreachable sources and synthetic records are in `results/facts.json`, which `python -m pipeline facts` computes from the data files.

## 1. Real public dataset (`data/real/`)

### What it is
A ledger of public commitments on federal and Abu Dhabi AI transformation, with the evidence and claims that relate to them. It consists of:

| File | Content |
|---|---|
| `sources.json` | One record per public source: title, publisher, URL, source kind, publication date (or a note explaining why there is none), retrieval date, extraction note path, SHA-256 of the note, an `ai_assisted` flag, and the figures expected present or absent on the live page |
| `extracts/` | One extraction note per source |
| `commitments.json` | What an official source says a government will do, deliver, spend, expect or assess, with kind, target, unit, deadline precision, owner, measurement source, undefined terms and anchors |
| `evidence.json` | Reported activity or progress linked to commitments, with a corroboration label and an anchor |
| `claims.json` | Figures found in secondary reporting, held apart from status, with a label describing what was checked |
| `searchlog.json` | Where and when searches were run, which commitments they covered and what was found |
| `verification.json` | Results of checking each source against its live page |
| `blind_extraction.json` | A second, independent extraction pass used for the agreement analysis in `docs/EVALUATION.md` |

The names of the publishers and the full list of sources with their URLs are given in `docs/CONTEXT.md`. Other documents refer to them by type: official sources, an Abu Dhabi government entity, a federal statement, secondary media.

### How it was collected
- Sources were collected on 2026-10-09 through a web fetch tool that returns a generated extraction of each page, not the raw page. Extraction was model assisted, as stated in `docs/LIMITATIONS.md`. The extraction notes in `data/real/extracts/` were written during collection.
- Searches for progress evidence are recorded in `data/real/searchlog.json`. Earlier research that was not logged is noted in that file.
- Official sources were sought before secondary media. A commitment is taken from an official source; reported achievements are recorded as evidence, not as commitments.
- Data updates are reviewed commits. There is no live scraping.

### Provenance by hash and anchor
- Each source has a SHA-256 hash of its extraction note, computed with line endings normalised to LF.
- Each commitment, evidence item and claim carries a short anchor phrase that must appear in the note for its source.
- `python -m pipeline validate` fails on a stale hash, a missing anchor, an unknown reference, or media evidence labelled official.
- `python -m pipeline verify-live` fetches each source page on a networked machine and checks that the figures the note relies on are present, and that figures which should be absent are absent. A page that blocks automated requests is reported as unreachable, never as verified.
- The reasoning is recorded in `docs/adr/0004-hash-and-anchor-provenance.md`.

### What is not stored
- Page text, images, PDFs and full quotations. Nothing is mirrored or cached.
- Any personal data.
- Anything a source page did not support. Pages that could not be retrieved are not used as evidence.

The sources policy, including the takedown and correction path, is in `docs/SOURCES_POLICY.md` and `docs/CORRECTIONS.md`.

### Grading of sources and evidence
- **Source kind.** `official-statement` (an announcement of a policy, target or decision), `official-self-report` (an entity reporting its own progress), `secondary-media` (news or trade reporting) and `third-party` (independent assessment).
- **Corroboration.** `official-confirmed` (found in an official source), `single-source` (one non official source only) and `not-in-official-statement` (in media, absent from the official statement checked).
- **Eligibility for status.** Evidence from secondary media never moves a status unless an official source confirms it (`docs/adr/0003-media-only-evidence-excluded.md`).
- **Flags.** `ai_assisted` marks a source that states it was produced with AI assistance. A status records whether all its evidence is an official self report, and evidence older than 180 days is flagged stale.

### Known gaps
- Some sources could not be reached by the live verifier and are reported as unreachable. The current number is the `sources.unreachable` entry in `results/facts.json`.
- Some pages could not be retrieved during collection and are not used.
- Some figures circulate in secondary reporting but were not found in the official statement checked. They are kept in the claim register and excluded from status.
- No independent third party corroboration of any progress claim was found in the sources reviewed. This is a finding about the sources reviewed, not proof that none exists.
- The extraction notes and the Arabic text have not been reviewed by a person other than the author (`docs/REVIEW_CHECKLIST.md`).
- Agreement with the second extraction pass is a consistency check between extractors, not independent human validation.

### Licence
The dataset is released under CC BY 4.0. Source material remains the property of its publishers. The repository stores URLs, retrieval dates, short anchors and extraction notes, not republished text.

## 2. Synthetic registry (`data/synthetic/`)

**This dataset is synthetic. Nothing in it describes a real entity, service or system.**

### Purpose
To exercise the Definition Lab and the maturity and governance views on a population whose properties are known, so the effect of a definition can be shown without touching sensitive operational data.

### Composition
- Synthetic entities across sectors. By default the generator creates 16 entities spread over 8 sectors, each with an `advancement` value in [0, 1].
- Synthetic items, each a `service` (citizen or business facing) or an `operation` (internal). The number of items per entity is drawn around a generator parameter of 38. The exact counts are in `data/synthetic/registry.json` and in the `registry.entities` and `registry.items` entries of `results/facts.json`.
- Per item: annual transactions, an automation maturity level 0 to 4 (our proposed ladder, not an official one), and four governance flags: human oversight, audit trail, UAE data residency, fallback to a person.

### Generation
`pipeline/synth.py`, seed `20260423`, Python `random.Random`. Maturity is drawn around each entity's advancement. Guardrail flags are more likely at higher maturity, but not reliably. Transaction volumes are log normal. Regenerate with `python -m pipeline synth`. A test fails if the committed file differs from the generator output.

### Known limits
- The shape of the distributions is an assumption. They were not fitted to real data.
- The results of the Definition Lab on this registry show how much a definition can move a percentage. They are not an estimate of any real percentage.
- Entity names are generic and deliberately do not resemble any real entity.

### Safeguards
`is_synthetic` is `Literal[True]` in the schema, so an unlabelled record cannot load. The site shows a persistent badge on every view that uses this data. Real and synthetic records are never combined in one number (`docs/adr/0005-synthetic-and-real-never-combined.md`).

### Licence
CC BY 4.0.

## 3. User uploaded files

- A user can upload a CSV of their own service inventory to the Definition Lab and related views. The file is parsed and processed in the browser only.
- The file is never sent anywhere and never stored by Mutabaa. The site has no network code path for uploads, and its Content-Security-Policy limits connections to its own origin. The data is held in page memory while the page is open and is not written to browser storage; the only values the site keeps in browser storage are the language and theme preferences.
- The browser engine caps the number of rows it reads and shows a message when a file is truncated. Uploaded content is rendered as text, and exports neutralise CSV formula prefixes (`docs/SECURITY.md`).
- Results computed on an uploaded file belong to the user. They are not combined with the real ledger or with the synthetic registry.
