"""Is the 'same target, very different answer' finding an artefact of one synthetic registry?

Generate many registries under different seeds, sizes and advancement profiles. For each, compute the
share under all 72 definitions. Report how often the 50% verdict flips depending on the definition,
and how much of the variance each of the four definition choices explains.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import product

from .sensitivity import sweep
from .stats import quantile
from .synth import generate

SEEDS = range(1, 61)
SIZES = (8, 16, 32)
PROFILES = {"low": (1.5, 3.5), "mid": (2.2, 2.0), "high": (3.5, 1.5)}
AXES = ("unit", "scope", "threshold", "guardrails")


def first_order_effects(rows: list[dict]) -> dict[str, float]:
    """Share of the variance of `share` across definitions explained by each axis alone (eta squared)."""
    vals = [r for r in rows if r["share"] is not None]
    mean = sum(r["share"] for r in vals) / len(vals)
    total = sum((r["share"] - mean) ** 2 for r in vals)
    out = {}
    for ax in AXES:
        groups = defaultdict(list)
        for r in vals:
            groups[r[ax]].append(r["share"])
        between = sum(len(g) * (sum(g) / len(g) - mean) ** 2 for g in groups.values())
        out[ax] = between / total if total else 0.0
    return out


def run() -> dict:
    per = []
    for (pname, adv), n, seed in product(PROFILES.items(), SIZES, SEEDS):
        reg = generate(seed=seed, n_entities=n, adv=adv)
        rows = sweep(reg)
        v = [r["share"] for r in rows if r["share"] is not None]
        core = quantile(v, 0.9) - quantile(v, 0.1)
        eff = first_order_effects(rows)
        per.append(
            {
                "profile": pname,
                "entities": n,
                "seed": seed,
                "min": min(v),
                "max": max(v),
                "meets": sum(x >= 0.5 for x in v),
                "defs": len(v),
                "core_spread": core,
                **{f"eta_{k}": e for k, e in eff.items()},
            }
        )
    spreads = [p["max"] - p["min"] for p in per]
    flips = [p for p in per if p["min"] < 0.5 <= p["max"]]
    by_profile = {}
    for name in PROFILES:
        sub = [p for p in per if p["profile"] == name]
        by_profile[name] = {
            "registries": len(sub),
            "flip_rate": round(sum(1 for p in sub if p["min"] < 0.5 <= p["max"]) / len(sub), 4),
            "median_spread": round(quantile([p["max"] - p["min"] for p in sub], 0.5), 4),
            "median_core_spread": round(quantile([p["core_spread"] for p in sub], 0.5), 4),
        }
    return {
        "registries": len(per),
        "profiles": {k: list(v) for k, v in PROFILES.items()},
        "sizes": list(SIZES),
        "seeds": [SEEDS.start, SEEDS.stop - 1],
        "flip_rate": round(len(flips) / len(per), 4),
        "spread": {q: round(quantile(spreads, q), 4) for q in (0.05, 0.5, 0.95)},
        "core_spread": {q: round(quantile([p["core_spread"] for p in per], q), 4) for q in (0.05, 0.5, 0.95)},
        "min_share": {q: round(quantile([p["min"] for p in per], q), 4) for q in (0.05, 0.5, 0.95)},
        "max_share": {q: round(quantile([p["max"] for p in per], q), 4) for q in (0.05, 0.5, 0.95)},
        "effects": {ax: round(sum(p[f"eta_{ax}"] for p in per) / len(per), 4) for ax in AXES},
        "by_profile": by_profile,
        "note": (
            "Synthetic registries only. This tests whether the finding depends on one seed or one set of "
            "generator assumptions. It says nothing about any real entity."
        ),
    }
