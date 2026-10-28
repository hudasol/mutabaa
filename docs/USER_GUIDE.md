# User guide

Mutabaa answers one question about a public commitment: could someone outside the owning office check it from
public information? It does not say whether the commitment is being met. This guide is for an analyst who wants
to use it on a commitments file, in the browser or from a terminal.

## What you need

- A browser, for the web app. Nothing is installed and nothing leaves your computer.
- Or Python 3.12 or newer, for the command line: `pip install -e .` from a clone of the repository.

## 1. Prepare a file

One row (or one object) per commitment. Three fields are required: `id`, `title` and `kind`. Run
`mutabaa template` or use "Download template" on the My commitments page to get the columns with an example row.

| Field | Write |
| --- | --- |
| `kind` | `target` (a number to reach), `milestone`, `deliverable`, `input`, `projection`, `assessment` or `vision` |
| `target_number` | A plain number. `1,200` and `50%` are accepted. Leave empty for a deliverable |
| `unit` | What is counted, such as `services` |
| `deadline` | `2027-12-31`, `31 Dec 2027`, `Q4 2027`, `2027-12` or `2027` count as dated. `within two years` does not |
| `owner` | The entity accountable. Leave empty if none is named |
| `measurement_source` | The report or dataset that would measure it. Leave empty if none is named |
| `undefined_terms` | Words the commitment relies on without defining them, separated by `;` |

Files from Excel work as they are: CSV with commas or semicolons, tab separated text, and "Unicode text"
(UTF-16). A cell may contain line breaks if it is quoted. Column names may differ; the page lets you match them
by hand, and the command line recognises common synonyms.

## 2. Read the result

Each commitment passes or fails up to six checks: a number, a unit, a dated deadline, a named owner, a way to
measure it, and no undefined terms. A deliverable or an assessment is not expected to have a number or a unit, so
those two checks are left out for it instead of counted against it. The share of applicable checks passed gives
one of three bands:

| Band | Share passed |
| --- | --- |
| Fully specified | 80% or more |
| Partly specified | 50% or more |
| Under-specified | less than 50% |

A band describes how precisely a commitment is worded. It is not a judgement on the office that made it. For each
missing check the tool writes a question in English and Arabic that the owning office could answer to close the gap.

## 3. Use it

In the browser, open My commitments, choose the file, read the table and the questions, and use "Export
questions (CSV)" to take them into a document or a spreadsheet.

From a terminal:

```
mutabaa score commitments.csv --questions --lang both
mutabaa score commitments.csv --format json > scored.json
mutabaa score commitments.csv --strict --min-ratio 0.5     # exit code 1 if a row is malformed or a score is low
```

See [CLI.md](CLI.md) for every option and exit code.

## What the tool will not tell you

- Whether a commitment was met. A status needs public evidence, and the My commitments page assigns none.
- Whether a commitment is a good one. A precise target can still be a poor target.
- Anything about an office beyond the wording of the file you gave it.

## If something looks wrong

A row that cannot be read is listed with its row number and the reason, and the rest of the file is still scored.
Files above 200,000 rows are cut at that limit and the page and the command line say so. If a file will not load at
all, the message names the cause (not valid JSON, a missing required column, no rows).
