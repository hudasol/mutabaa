# Sources policy

Not legal advice. Needs review by counsel before any external use (open item in `docs/reviews/04-programme-office-lens.md`).

## What is stored
- A short extraction **note** for each source page. The notes are paraphrases prepared during collection from summaries returned by a web fetch tool, with automated help (see `docs/LIMITATIONS.md`). They do not reproduce page text; anchors are under 15 words.
- The SHA-256 hash of that note, the source URL, the publisher, the page date, and the retrieval date.
- Short **anchors** (a few words) that must appear in the note, so a reader can find the passage on the source page.
- Expected figures per source (`expect_present`, `expect_absent`) used by `verify-live`.

## What is not stored
- Page text, images, PDFs, or full quotations. Nothing is mirrored or cached.
- Personal data, apart from the names and titles of public officials where an official statement names them in their official role. Registry fields contain no personal data by design.

## How pages are accessed
- `verify-live` reads each host's `robots.txt` first and does not fetch a page it disallows. It makes plain GET requests with an honest User-Agent, TLS verification on, a pause between pages and retries with back off. It does not get around a refusal (403, robots, paywall): such a page is reported *unreachable*, not *verified*.
- Pages the maintainer could not read directly are recorded as leads in `docs/CONTEXT.md`, not as evidence.

## Media sources
Media reports are listed with what was checked. They never change a status unless an official statement confirms the figure.

## Takedown and correction
Anyone, including the publisher, can ask for a source entry, note or anchor to be changed or removed. Use the correction template (`docs/CORRECTIONS.md`). Removal requests are actioned first and discussed after, within 2 working days.

## Licence
Code: MIT. Dataset files in `data/` (including the extraction notes, paraphrases prepared with automated help as described above): CC BY 4.0, as stated in the README and `docs/DATA_STATEMENT.md`. Source content remains with its publishers.
