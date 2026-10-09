"""Deterministic status engine.

Rules, in order. The default is neutral: absence of public evidence is not failure.
"""

from __future__ import annotations

from datetime import date

from .schemas import Commitment, Evidence, Source, StatusResult

NON_OUTCOME_KINDS = ("vision", "projection", "assessment")


def eligible(e: Evidence, sources: dict[str, Source]) -> bool:
    """Media-only evidence never moves a status."""
    return sources[e.source_id].kind != "secondary-media" or e.corroboration == "official-confirmed"


def status(c: Commitment, evidence: list[Evidence], sources: dict[str, Source]) -> StatusResult:
    mine = [e for e in evidence if c.id in e.commitment_ids]
    ok = [e for e in mine if eligible(e, sources)]
    excluded = [e.id for e in mine if not eligible(e, sources)]

    def result(st, reasons, **kw):
        return StatusResult(
            commitment_id=c.id,
            status=st,
            reasons=reasons,
            evidence_ids=[e.id for e in ok],
            excluded_evidence_ids=excluded,
            self_reported_only=bool(ok)
            and all(sources[e.source_id].kind == "official-self-report" for e in ok),
            unit_mismatch=kw.get("unit_mismatch", False),
            progress_ratio=kw.get("ratio"),
            progress_as_of=kw.get("as_of"),
        )

    if c.kind in NON_OUTCOME_KINDS:
        return result(
            "not-checkable", [f"kind '{c.kind}' is not an outcome that can be delivered or missed"]
        )
    if not ok:
        why = ["no eligible public evidence"]
        if excluded:
            why.append(f"{len(excluded)} media-only item(s) excluded")
        return result("no-public-evidence", why)

    comparable = [
        e
        for e in ok
        if e.kind == "quantified-progress"
        and e.value is not None
        and c.unit is not None
        and e.unit == c.unit
        and c.target_number
    ]
    mismatch = any(e.kind == "quantified-progress" and e.unit != c.unit for e in ok)
    if comparable:
        latest = max(comparable, key=lambda e: (e.as_of is not None, e.as_of or date.min))
        ratio = latest.value / c.target_number
        claimed = any(e.kind == "target-met-claim" for e in ok)
        st = "target-claimed-met" if claimed else "milestone-reported"
        return result(
            st,
            [f"{latest.value:g} of {c.target_number:g} {c.unit} reported"],
            ratio=round(ratio, 4),
            as_of=latest.as_of,
            unit_mismatch=mismatch,
        )
    reasons = ["activity reported without a figure comparable to the target"]
    if mismatch:
        reasons.append("reported figure is in a different unit from the target")
    return result("activity-reported", reasons, unit_mismatch=mismatch)
