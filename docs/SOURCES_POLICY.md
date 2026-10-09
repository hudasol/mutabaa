# Sources policy

Not legal advice. Needs review by counsel before any external use (open item in `docs/reviews/04-atrc.md`).

## What is stored
- A short extraction **note** written by the maintainer in their own words, for each source page.
- The SHA-256 hash of that note, the source URL, the publisher, the page date, and the retrieval date.
- Short **anchors** (a few words) that must appear in the note, so a reader can find the passage on the source page.
- Expected figures per source (`expect_present`, `expect_absent`) used by `verify-live`.

## What is not stored
- Page text, images, PDFs, or full quotations. Nothing is mirrored or cached.
- Any personal data. Registry fields contain no personal data by design.

## How pages are accessed
- `verify-live` makes plain GET requests with an honest User-Agent, TLS verification on, retries with back-off. It does not get around a refusal (403, robots, paywall): such a page is reported *unreachable*, not *verified*.
- Pages the maintainer could not read directly are recorded as leads in `docs/LEADS.md`, not as evidence.

## Media sources
Media reports are listed with what was checked. They never change a status unless an official statement confirms the figure.

## Takedown and correction
Anyone, including the publisher, can ask for a source entry, note or anchor to be changed or removed. Use the correction template (`docs/CORRECTIONS.md`). Removal requests are actioned first and discussed after, within 2 working days.

## Licence
Code: MIT. Extraction notes and analysis text: written by the maintainer and released with the repository under the same licence. Source content remains with its publishers.
