# Arabic review kit

Status: open. No native Arabic speaker has reviewed the Arabic text of this project. The Arabic was written by the author and the terms are listed in `data/glossary/glossary.json`. Every Arabic string on the site should be treated as a draft until the table below is filled in.

## What we ask of a reviewer

1. Open `arabic_strings.csv` (UTF-8, readable in any spreadsheet program). It holds every interface string with the English source, the Arabic text and the glossary terms involved.
2. In the column `reviewer_verdict` write `ok` or `change`. For `change`, write the corrected Arabic in `reviewer_correction` and, if useful, a reason in `reviewer_note`.
3. Review the ten glossary terms first. They recur in most strings, so a change there decides many rows. Questions for each term:
   - Is the term the one an Arabic reader in the public sector would expect?
   - Is the register formal and neutral, without advocacy?
   - Does it read correctly beside a number (counts, dates, percentages)?
4. Check right to left behaviour on the live site: switch the language to Arabic, open each page and note any text that is cut, mirrored wrongly or mixed in direction.

## What is not asked

The reviewer is not asked to endorse the project, to judge its method or to be named anywhere. A reviewer who wishes to be credited may say so; otherwise the review is recorded without a name.

## Returning the review

Send back the filled CSV to the author. The author then applies the corrections in `site/src/i18n.ts` and `data/glossary/glossary.json`, sets `reviewed_by_native_speaker` to `true` only after a full pass, and records the date in `CHANGELOG.md`. Until then the README status table keeps the item open.

## Regenerating the CSV

`cd site && npm run review-kit` rewrites `arabic_strings.csv` from the current strings. A test fails when the file is out of date.
