# Human review checklist

Mutabaa's extraction notes were written by a model from public pages and have not been verified by a person. Before any external use, a reviewer should complete this list. About two hours.

1. Open each of the 12 URLs in `data/real/sources.json`. Confirm the page still says what its extraction note says. Record any difference in a new `docs/REVIEW_LOG.md`.
2. For each commitment, open `C##` in the ledger and confirm that the quoted anchor matches the page.
3. Check the five claims (K01 to K05): look in the official statement (S01) and in other official pages for the figure. If found, change its corroboration and re-run `python -m pipeline validate`.
4. Check the Arabic titles and statements with a native Arabic reader (UI strings in `site/src/i18n.ts` too).
5. Confirm the six checks in `docs/METHODOLOGY.md` are the ones a government analyst would ask.
6. Look for newer statements than 9 October 2026 and add them as sources.
7. Decide whether the maturity ladder (L0 to L4) is useful as written, or replace it with an official classification if one is published.

After a change to a note: `python -m pipeline rehash`, then `python -m pipeline build`, then commit `site/src/data/real.json` with it.
