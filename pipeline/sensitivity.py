"""How much does 'X% of government is agentic' change with the definition?

A definition is four choices: the unit counted, the scope, the maturity threshold and whether
guardrails are required. The result for a definition is the share of the population that qualifies.
The TypeScript engine in site/src/engine mirrors this file; a golden file keeps them identical.
"""

from __future__ import annotations

from itertools import product
from typing import get_args

from .schemas import Definition, Guardrails, Registry, Scope, ServiceItem, Threshold, Unit

SECTOR_SHARE_REQUIRED = 0.5  # an entity or sector counts as "transformed" when this share qualifies


def in_scope(it: ServiceItem, scope: str) -> bool:
    if scope == "citizen-services":
        return it.kind == "service" and it.audience == "citizen"
    if scope == "all-services":
        return it.kind == "service"
    return True


def qualifies(it: ServiceItem, threshold: int, guardrails: str) -> bool:
    if it.maturity < threshold:
        return False
    if guardrails == "required":
        return it.oversight and it.audit_trail and it.uae_residency and it.fallback
    return True


def share(reg: Registry, d: Definition) -> float | None:
    items = [i for i in reg.items if in_scope(i, d.scope)]
    if not items:
        return None
    if d.unit == "services":
        return sum(qualifies(i, d.threshold, d.guardrails) for i in items) / len(items)
    if d.unit == "transactions":
        total = sum(i.annual_transactions for i in items)
        if total == 0:
            return None
        return (
            sum(i.annual_transactions for i in items if qualifies(i, d.threshold, d.guardrails))
            / total
        )
    key = "entity_id" if d.unit == "entities" else "sector"
    groups: dict[str, list[ServiceItem]] = {}
    for i in items:
        groups.setdefault(getattr(i, key), []).append(i)
    ok = 0
    for g in groups.values():
        q = sum(qualifies(i, d.threshold, d.guardrails) for i in g)
        if q / len(g) >= SECTOR_SHARE_REQUIRED:
            ok += 1
    return ok / len(groups)


def all_definitions() -> list[Definition]:
    return [
        Definition(unit=u, scope=s, threshold=t, guardrails=g)
        for u, s, t, g in product(
            get_args(Unit), get_args(Scope), get_args(Threshold), get_args(Guardrails)
        )
    ]


def sweep(reg: Registry) -> list[dict]:
    rows = []
    for d in all_definitions():
        v = share(reg, d)
        rows.append({**d.model_dump(), "share": None if v is None else round(v, 6)})
    return rows


def summary(rows: list[dict], target: float = 0.5) -> dict:
    vals = [r["share"] for r in rows if r["share"] is not None]
    return {
        "definitions": len(rows),
        "min": min(vals),
        "max": max(vals),
        "target": target,
        "meet_target": sum(v >= target for v in vals),
    }
