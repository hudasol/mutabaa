# Corrections and right of reply

Mutabaa grades how checkable public commitments are and what the public record supports. It can be wrong. Entities, publishers and readers can say so.

## How to submit
Open an issue with the **Correction** template: https://github.com/hudasol/mutabaa/issues/new?template=correction.yml

Include the commitment or source ID, what is wrong, and a public link that shows it. Evidence that is not public cannot change a status, but it can change a question we ask.

## What happens
| Step | Time |
|---|---|
| Acknowledged | 2 working days |
| Takedown requests actioned | 2 working days |
| Factual errors (wrong figure, date, owner, source) fixed or answered | 5 working days |
| Disagreements about wording or interpretation | Answered in writing within 10 working days; the reply is linked from the commitment if the person asks |

## Rules
- A correction that changes a status or a score is a data change and follows `CONTRIBUTING.md`: hash updated, `verify-live` run, `python -m pipeline diff` pasted in the pull request.
- The change is recorded in `CHANGELOG.md`, so the history of what was wrong is public.
- An entity's own public statement can be added as evidence like any other official source.
