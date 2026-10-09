# Contributing

## Who may change what
| Change | Who | Review |
|---|---|---|
| Code, tests, docs | Anyone | One review |
| A status, score, or source record | Maintainer or a named reviewer | Second person checks the source page |
| Arabic text | A native speaker | Reviewer who was not the author |

## Rules
1. Extraction notes are written in your own words. Never paste page text.
2. Every figure in a note must also be listed under `expect_present` for its source so `verify-live` can check it.
3. A commitment's `anchors` must appear in the stored note. The validator enforces this.
4. "No public evidence" needs a search-log entry (where, when, what was found).
5. Media-only evidence never moves a status.
6. Synthetic data stays labelled and is never mixed with public-source numbers.

## Workflow
```
python -m pipeline validate
python -m pipeline rehash          # after editing a note
python -m pipeline verify-live --only S03
python -m pipeline build
python -m pipeline diff HEAD
make test
```
Paste the `diff` output into the pull request. See `docs/CORRECTIONS.md` for corrections from outside.
