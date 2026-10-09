# Datasheet: Mutabaa synthetic registry

**This dataset is synthetic. Nothing in it describes a real entity, service or system.**

## Purpose
To exercise the Definition Lab and the maturity and governance views on a population whose properties are known, so the effect of a definition can be shown without touching sensitive operational data.

## Composition
- 16 synthetic entities across 8 sectors, each with an `advancement` value in [0, 1].
- About 570 synthetic items, each a `service` (citizen- or business-facing) or an `operation` (internal).
- Per item: annual transactions, an automation maturity level 0 to 4 (our proposed ladder, not an official one), and four governance flags: human oversight, audit trail, UAE data residency, fallback to a person.

## Generation
`pipeline/synth.py`, seed `20260423`, Python `random.Random`. Maturity is drawn around each entity's advancement. Guardrail flags are more likely at higher maturity, but not reliably. Transaction volumes are log-normal. Regenerate with `python -m pipeline synth`. A test fails if the committed file differs from the generator output.

## Known limits
- The shape of the distributions is an assumption. They were not fitted to real data.
- The results of the Definition Lab on this registry show how much a definition can move a percentage. They are not an estimate of any real percentage.
- Entity names are generic and deliberately do not resemble any real entity.

## Safeguards
`is_synthetic` is `Literal[True]` in the schema, so an unlabelled record cannot load. The site shows a persistent badge on every view that uses this data. Real and synthetic records are never combined in one number.

## Licence
CC BY 4.0.
