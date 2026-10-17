# ADR 0002: Neutral default status

## Status
Accepted.

## Context
The ledger gives each commitment a status. Public sources rarely report progress against a target, and internal tracking inside government will know more than public sources do. If an absence of public evidence were shown as failure, the tool would make claims about government performance that the data cannot support, and a reader could take a gap in publication for a gap in delivery.

## Options considered
1. A traffic light status (for example on track, at risk, off track) inferred from the evidence found.
2. A status that starts negative and improves as evidence is found.
3. A status that starts neutral and only describes what public evidence exists, with written rules applied in a fixed order.

## Decision
We chose option 3, implemented in `pipeline/status.py`. The rules are applied in order:
1. A commitment whose kind is vision, projection or assessment is `not-checkable`, because it is not an outcome that can be delivered or missed.
2. Evidence that is not eligible is set aside (see ADR 0003). If no eligible evidence is left, the status is `no-public-evidence`.
3. A reported figure in the same unit as the target gives `milestone-reported` with a progress ratio, or `target-claimed-met` when the source claims the target is met.
4. Otherwise the status is `activity-reported`. A figure in a different unit is flagged and never converted.

The status also carries flags rather than verdicts: whether all eligible evidence is an official self report, whether the latest evidence is older than 180 days (`STALE_AFTER_DAYS`), and which items were excluded.

## Consequences
- `no-public-evidence` means "nothing public was found that maps to this target", not "not done". The interface and `docs/LIMITATIONS.md` say so.
- The search log in `data/real/searchlog.json` records where and when searches were run, so the neutral status can be read as "searched these places on this date, found nothing".
- The status never says whether a commitment is on track. A reader who wants that judgement has to bring other information.
- Because the rules are deterministic, the same data always gives the same status, and a reviewer can trace each status to the reasons listed with it.
