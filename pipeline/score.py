"""Verifiability score: can a third party check this commitment from public information?

Six yes/no checks. A check that does not apply to a kind of commitment is excluded, not failed.
The score says nothing about whether the commitment is being met.
"""

from __future__ import annotations

from .schemas import Commitment, VerifiabilityResult

CHECKS = (
    "numeric_target",
    "unit_defined",
    "dated_deadline",
    "owner_named",
    "measurement_source",
    "terms_defined",
)

LABELS = {
    "numeric_target": "A number to reach",
    "unit_defined": "A defined unit",
    "dated_deadline": "A dated deadline",
    "owner_named": "A named owner",
    "measurement_source": "A named way to measure it",
    "terms_defined": "No undefined terms",
}

_NO_NUMBER_NEEDED = ("deliverable", "assessment")


def score(c: Commitment) -> VerifiabilityResult:
    numeric_applies = c.kind not in _NO_NUMBER_NEEDED
    checks: dict[str, bool | None] = {
        "numeric_target": (c.target_number is not None) if numeric_applies else None,
        "unit_defined": (c.unit is not None) if numeric_applies else None,
        "dated_deadline": c.deadline_precision in ("day", "month", "year"),
        "owner_named": c.owner is not None,
        "measurement_source": c.measurement_source is not None,
        "terms_defined": len(c.undefined_terms) == 0,
    }
    applicable = [v for v in checks.values() if v is not None]
    passed = sum(1 for v in applicable if v)
    ratio = passed / len(applicable)
    band = (
        "checkable" if ratio >= 0.8 else "partly-checkable" if ratio >= 0.5 else "not-yet-checkable"
    )
    missing = [k for k, v in checks.items() if v is False]
    return VerifiabilityResult(
        commitment_id=c.id,
        checks=checks,
        applicable=len(applicable),
        passed=passed,
        ratio=round(ratio, 4),
        band=band,
        missing=missing,
    )
