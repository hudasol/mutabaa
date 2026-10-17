# Architecture decision records

These records explain the main design choices in Mutabaa: the problem each choice addresses, the options we considered, what we decided and what follows from it. Mutabaa is a student prototype and a proposal seed, not a deployment, and nothing in these records implies endorsement by any entity. Shorter dated decisions are kept in `docs/DECISIONS.md`, and the wider design is described in `docs/ARCHITECTURE.md`.

| Record | Summary |
|---|---|
| [0001 Static by design](0001-static-first-design.md) | The browser is the only runtime: no server, no runtime network call, no secrets. |
| [0002 Neutral default status](0002-neutral-default-status.md) | Status starts at `no-public-evidence` and describes public evidence, never performance. |
| [0003 Media only evidence excluded](0003-media-only-evidence-excluded.md) | Secondary media evidence moves no status unless an official source confirms it. |
| [0004 Provenance by hash and anchor](0004-hash-and-anchor-provenance.md) | Each source has a hashed extraction note, and every record has an anchor found in that note. |
| [0005 Synthetic and real never combined](0005-synthetic-and-real-never-combined.md) | The synthetic registry is labelled, stored apart and never mixed with real data in one number. |
| [0006 No model at runtime](0006-no-runtime-model.md) | Scores, statuses and sweeps follow written rules; no model runs in the build or the browser. |
| [0007 Band names describe the wording](0007-band-names-describe-wording.md) | Score bands are labelled by how a commitment is worded, not as a verdict on its owner. |
| [0008 Hash pinned offline build](0008-hash-pinned-offline-build.md) | The offline file inlines its code and allows only those inline blocks by their SHA-256. |
