# Performance

Measured on one development machine on 2026-10-28. Timings depend on the machine; the guards in the test suite use
ceilings several times higher so that a slow runner passes and an accidental quadratic loop does not.

## Reading and scoring a large file

A generated file of 200,000 rows (the row cap), about 20 MB, ten columns, a quoted title with a comma on every row.

| Where | What | Time |
| --- | --- | --- |
| `mutabaa` (Python 3.12) | read and convert | about 5 s |
| `mutabaa` (Python 3.12) | score and build questions | about 2.5 s |
| Browser reader (Node, same code as the page) | read, convert and score | about 1.3 s |

Reproduce with `python scripts/benchmark.py [ROWS]` and `npm test -- src/perf.test.ts` in `site/`. A file with no
quotation marks at all takes a faster path in both readers and gives the same result.

Rows beyond 200,000 are not read. The page and the command line both say so.

## Site size

`npm run check:bundle` fails the build when a budget is exceeded. Sizes are gzip bytes.

| Part | Measured | Budget |
| --- | --- | --- |
| First script (React, data, strings) | about 96 kB | 110 kB |
| All scripts including lazily loaded pages | about 112 kB | 135 kB |
| Styles | about 4.5 kB | 6 kB |
| Offline single file (fonts included) | about 525 kB | 600 kB |

Each page is a separate chunk loaded on first visit. The offline file folds them back into one script, because it
must open from a local file with no other requests.

Most of the first script is the public data (`real.json`, about 337 kB before compression). It is kept in the
first script because every page reads it; loading it separately would add a loading state to every screen for a
saving of roughly 20 kB.
