# Command line reference

Install from a clone, then use the `mutabaa` command, or run `python -m pipeline` without installing.

```
pip install -e .
mutabaa --help
```

## Scoring your own file

```
mutabaa template > commitments.csv     # the columns, with one example row
mutabaa score commitments.csv          # a table: score, band and what each commitment lacks
mutabaa questions commitments.csv      # the same, with the questions that would close each gap
```

The file is UTF-8 CSV or JSON. A CSV may use commas, semicolons or tabs, and quoted cells may hold line breaks.
A JSON file is an array of objects or an object with a `commitments` array. Column names are matched by name or by
a few common synonyms (`name` for `title`, `due` for `deadline`, `type` for `kind`). The browser page reads the
same files with the same rules.

| Column | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Unique within the file |
| `title` | yes | What was promised |
| `kind` | yes | One of `target`, `milestone`, `deliverable`, `input`, `projection`, `assessment`, `vision` |
| `owner` | no | The entity accountable |
| `metric`, `unit`, `target_number` | no | What is counted and the number to reach |
| `deadline` | no | A calendar date, a month, a quarter or a year counts as dated; other text is relative |
| `measurement_source` | no | The dataset or report that would measure it |
| `undefined_terms` | no | Terms the commitment uses without defining them, separated by `;` |

### Options

| Option | Effect |
| --- | --- |
| `--format text`, `json` or `csv` | Output format. `json` includes a summary block; `csv` is one row per commitment |
| `--questions` | With `score`, also list the questions (`questions` always does) |
| `--lang en`, `ar` or `both` | Language of the questions in text output |
| `--strict` | Exit 1 if any row was rejected or the file was cut at the row limit |
| `--min-ratio R` | Exit 1 if any commitment scores below `R`, between 0 and 1 |

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 1 | A gate was not met (`--strict` or `--min-ratio`), or a check failed in `verify-live` |
| 2 | The input could not be read, or no row was usable |

`--min-ratio` looks only at rows that were read. A rejected row is not scored, so use `--strict` as well if a malformed
row should fail the run. Output is always UTF-8, so Arabic text survives a redirect on any platform.

These make the command usable in a pipeline: `mutabaa score plan.csv --strict --min-ratio 0.5` fails the build
when a row is malformed or a commitment is mostly unverifiable.

The score says whether a third party could check a commitment from public information. It says nothing about
whether the commitment is being met. See [METHODOLOGY.md](METHODOLOGY.md).

## Repository commands

| Command | Effect |
| --- | --- |
| `validate` | Integrity checks on the real data |
| `rehash` | Refresh source note hashes |
| `synth` | Regenerate the synthetic registry |
| `build` | Regenerate `site/src/data/real.json` |
| `analyse` | Recompute the exploratory analyses in `data/analysis/` |
| `facts` | Write `results/facts.json`, the numbers documents may cite |
| `evaluate` | Run the preregistered experiments, write `results/`, render `docs/EVALUATION.md` |
| `sync-docs` | Rewrite stale fact markers in the documents |
| `schema` | Write JSON Schema files to `schema/` |
| `golden` | Write the golden files the TypeScript port is tested against |
| `verify-live [--write] [--only IDS]` | Check source pages for the expected figures (needs network) |
| `diff [REF]` | Show what changed in the payload since a git ref |
