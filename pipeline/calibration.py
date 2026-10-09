"""How arbitrary is the verifiability score? Three checks, all computed from the committed data.

1. Band thresholds: how many commitments change band if the 80% / 50% cut-offs move?
2. Weights and checks: how stable is the ranking if checks are weighted differently or one is dropped?
3. Internal consistency: do the structured fields agree with a simple independent reading of the
   statement text? (Not human validation. It catches curation slips, not judgement errors.)
"""

from __future__ import annotations

import random
import re
from itertools import product

from .schemas import Commitment
from .score import CHECKS, score
from .stats import bootstrap_ci, cohen_kappa, quantile, spearman

HI = (0.7, 0.75, 0.8, 0.85, 0.9)
LO = (0.4, 0.45, 0.5, 0.55, 0.6)


def band(r: float, hi: float, lo: float) -> str:
    return "checkable" if r >= hi else "partly-checkable" if r >= lo else "not-yet-checkable"


def band_sensitivity(cs: list[Commitment]) -> dict:
    ratios = [score(c).ratio for c in cs]
    base = [band(r, 0.8, 0.5) for r in ratios]
    changed = []
    for hi, lo in product(HI, LO):
        changed.append(sum(band(r, hi, lo) != b for r, b in zip(ratios, base, strict=True)))
    return {
        "grid": len(changed),
        "max_changed": max(changed),
        "median_changed": quantile(changed, 0.5),
        "n": len(cs),
    }


def weighted(c: Commitment, w: dict[str, float], drop: str | None = None) -> float:
    s = score(c)
    num = den = 0.0
    for k, v in s.checks.items():
        if v is None or k == drop:
            continue
        den += w[k]
        num += w[k] * (1.0 if v else 0.0)
    return num / den if den else 0.0


def weight_stability(cs: list[Commitment], draws: int = 1000, seed: int = 11) -> dict:
    rng = random.Random(seed)
    eq = {k: 1.0 for k in CHECKS}
    base = [weighted(c, eq) for c in cs]
    rhos = []
    for _ in range(draws):
        w = {k: rng.expovariate(1.0) for k in CHECKS}  # a Dirichlet(1,...) draw up to scale
        r = spearman(base, [weighted(c, w) for c in cs])
        if r is not None:
            rhos.append(r)
    drops = {}
    for k in CHECKS:
        drops[k] = spearman(base, [weighted(c, eq, drop=k) for c in cs])
    pass_rate = {}
    for k in CHECKS:
        vals = [score(c).checks[k] for c in cs if score(c).checks[k] is not None]
        pass_rate[k] = round(sum(vals) / len(vals), 3) if vals else None
    return {
        "draws": len(rhos),
        "spearman_p05": round(quantile(rhos, 0.05), 3),
        "spearman_median": round(quantile(rhos, 0.5), 3),
        "leave_one_out": {k: (None if v is None else round(v, 3)) for k, v in drops.items()},
        "pass_rate": pass_rate,
    }


_NUM = re.compile(r"\d")
_YEAR = re.compile(r"\b20[2-4]\d\b")


def consistency(cs: list[Commitment]) -> dict:
    """Compare two structured fields with a regex reading of the commitment's own wording."""
    num_c = [c for c in cs if c.kind not in ("deliverable", "assessment")]
    a = [c.target_number is not None for c in num_c]
    b = [bool(_NUM.search(c.statement) or _NUM.search(c.title)) for c in num_c]
    k1 = cohen_kappa(a, b)
    ci1 = bootstrap_ci(len(a), lambda ix: cohen_kappa([a[i] for i in ix], [b[i] for i in ix]))
    a2 = [c.deadline_precision in ("day", "month", "year") for c in cs]
    b2 = [bool(_YEAR.search((c.deadline_text or "") + " " + c.statement)) for c in cs]
    k2 = cohen_kappa(a2, b2)
    ci2 = bootstrap_ci(len(a2), lambda ix: cohen_kappa([a2[i] for i in ix], [b2[i] for i in ix]))
    return {
        "numeric_target": {"n": len(a), "agree": sum(x == y for x, y in zip(a, b, strict=True)),
                           "kappa": None if k1 is None else round(k1, 3), "ci95": ci1},
        "dated_deadline": {"n": len(a2), "agree": sum(x == y for x, y in zip(a2, b2, strict=True)),
                           "kappa": None if k2 is None else round(k2, 3), "ci95": ci2},
        "disagreements": sorted(
            {c.id for c, x, y in zip(num_c, a, b, strict=True) if x != y}
            | {c.id for c, x, y in zip(cs, a2, b2, strict=True) if x != y}
        ),
    }


def run(cs: list[Commitment]) -> dict:
    return {
        "bands": band_sensitivity(cs),
        "weights": weight_stability(cs),
        "consistency": consistency(cs),
        "note": (
            "Computed from the curated fields. The consistency check compares two readings that both "
            "come from the same curation, so it finds slips, not judgement errors. Human validation is "
            "still outstanding."
        ),
    }
