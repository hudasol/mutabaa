"""Preregistered experiments E1 to E6 (see PREREGISTRATION.md). Run with `python -m pipeline evaluate`.

E5 and E6 live in evaluate_real.py.

Each experiment returns a dict with its results, its predictions marked HIT or MISS, and `facts`: the
numbers that docs/EVALUATION.md cites (picked up by pipeline/facts.py).
"""

from __future__ import annotations

import math
import random
import statistics
from collections.abc import Callable, Sequence

from .evaluate_real import e5, e6
from .io import load_real
from .robustness import AXES, PROFILES, SIZES, first_order_effects
from .schemas import Commitment, Registry, ServiceItem
from .score import score
from .sensitivity import in_scope, qualifies, sweep
from .stats import quantile, wilson
from .status import eligible
from .synth import generate
from .synth_b import generate_b

OFFICIAL = ("official-statement", "official-self-report")


def _fact(value, fmt: str) -> dict:
    return {"value": value, "format": fmt}


def _verdict(ok: bool) -> str:
    return "HIT" if ok else "MISS"


# --------------------------------------------------------------------------- E1


def auc(scores: Sequence[float], labels: Sequence[bool]) -> float | None:
    """Mann Whitney probability that a random positive scores above a random negative (ties count half)."""
    pos = [s for s, y in zip(scores, labels, strict=True) if y]
    neg = [s for s, y in zip(scores, labels, strict=True) if not y]
    if not pos or not neg:
        return None
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def auc_required(scores: Sequence[float], labels: Sequence[bool]) -> float:
    """Like auc, for data known to hold both classes."""
    v = auc(scores, labels)
    if v is None:
        raise ValueError("both classes are needed")
    return v


def auc_ci(scores, labels, reps: int = 2000, seed: int = 7) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(scores)
    vals = []
    for _ in range(reps):
        ix = [rng.randrange(n) for _ in range(n)]
        v = auc([scores[i] for i in ix], [labels[i] for i in ix])
        if v is not None:
            vals.append(v)
    return quantile(vals, 0.025), quantile(vals, 0.975)


def outcome(c: Commitment, d) -> bool:
    src = {s.id: s for s in d.sources}
    return any(
        c.id in e.commitment_ids and eligible(e, src) and src[e.source_id].kind in OFFICIAL
        for e in d.evidence
    )


def e1() -> dict:
    d = load_real()
    cs = d.commitments
    y = [outcome(c, d) for c in cs]
    s = [score(c).ratio for c in cs]
    point = auc_required(s, y)
    lo, hi = auc_ci(s, y)
    baselines: dict[str, float] = {
        "numeric_target": auc_required([float(c.target_number is not None) for c in cs], y),
        "number_and_deadline": auc_required(
            [
                float(c.target_number is not None and c.deadline_precision in ("day", "month", "year"))
                for c in cs
            ],
            y,
        ),
        "owner_named": auc_required([float(c.owner is not None) for c in cs], y),
    }
    rnd: list[float] = []
    for seed in range(1, 21):
        rng = random.Random(seed)
        rnd.append(auc_required([rng.random() for _ in cs], y))
    best = max(baselines.values())
    preds = {
        "P1a": {"text": "score AUC between 0.55 and 0.80", "result": _verdict(0.55 <= point <= 0.80)},
        "P1b": {"text": "lower end of the 95% interval below 0.50", "result": _verdict(lo < 0.50)},
        "P1c": {
            "text": "score AUC at least the best simple baseline minus 0.05",
            "result": _verdict(point >= best - 0.05),
        },
    }
    return {
        "n": len(cs),
        "positives": sum(y),
        "auc": round(point, 4),
        "ci95": [round(lo, 4), round(hi, 4)],
        "baselines": {k: round(v, 4) for k, v in baselines.items()},
        "random": {
            "mean": round(statistics.mean(rnd), 4),
            "p025": round(quantile(rnd, 0.025), 4),
            "p975": round(quantile(rnd, 0.975), 4),
            "seeds": [1, 20],
        },
        "predictions": preds,
        "facts": {
            "n": _fact(len(cs), "int"),
            "positives": _fact(sum(y), "int"),
            "auc": _fact(point, "f2"),
            "ci_low": _fact(lo, "f2"),
            "ci_high": _fact(hi, "f2"),
            "baseline.numeric_target": _fact(baselines["numeric_target"], "f2"),
            "baseline.number_and_deadline": _fact(baselines["number_and_deadline"], "f2"),
            "baseline.owner_named": _fact(baselines["owner_named"], "f2"),
            "random.mean": _fact(statistics.mean(rnd), "f2"),
            "random.p025": _fact(quantile(rnd, 0.025), "f2"),
            "random.p975": _fact(quantile(rnd, 0.975), "f2"),
            **{f"{k}": _fact(v["result"], "str") for k, v in preds.items()},
        },
    }


# --------------------------------------------------------------------------- E2


def _study(make: Callable[[str, int, int], Registry]) -> dict:
    per = []
    for pname in PROFILES:
        for n in SIZES:
            for seed in range(1, 61):
                rows = sweep(make(pname, n, seed))
                v = [r["share"] for r in rows if r["share"] is not None]
                per.append({"profile": pname, "min": min(v), "max": max(v), **first_order_effects(rows)})
    spreads = [p["max"] - p["min"] for p in per]

    def flips(sub):
        return sum(1 for p in sub if p["min"] < 0.5 <= p["max"]) / len(sub)

    return {
        "registries": len(per),
        "flip_rate": round(flips(per), 4),
        "by_profile": {k: round(flips([p for p in per if p["profile"] == k]), 4) for k in PROFILES},
        "spread": {q: round(quantile(spreads, float(q)), 4) for q in ("0.05", "0.5", "0.95")},
        "effects": {ax: round(statistics.mean(p[ax] for p in per), 4) for ax in AXES},
    }


def e2() -> dict:
    import json

    from .io import ROOT

    b = _study(lambda prof, n, seed: generate_b(seed=seed, n_entities=n, profile=prof))
    rb = json.loads((ROOT / "data" / "analysis" / "robustness.json").read_text(encoding="utf-8"))
    a = {
        "registries": rb["registries"],
        "flip_rate": rb["flip_rate"],
        "by_profile": {k: rb["by_profile"][k]["flip_rate"] for k in PROFILES},
        "spread": rb["spread"],
        "effects": rb["effects"],
    }
    top = max(b["effects"], key=b["effects"].get)
    preds = {
        "P2a": {
            "text": "flip rate under B between 0.60 and 0.95",
            "result": _verdict(0.60 <= b["flip_rate"] <= 0.95),
        },
        "P2b": {
            "text": "median spread under B at least 0.50",
            "result": _verdict(b["spread"]["0.5"] >= 0.50),
        },
        "P2c": {
            "text": "maturity threshold has the largest variance share under B",
            "result": _verdict(top == "threshold"),
        },
        "P2d": {
            "text": "low profile flips less often than high profile under B",
            "result": _verdict(b["by_profile"]["low"] < b["by_profile"]["high"]),
        },
    }
    facts = {}
    for name, res in (("a", a), ("b", b)):
        facts[f"{name}.registries"] = _fact(res["registries"], "int")
        facts[f"{name}.flip_rate"] = _fact(res["flip_rate"], "pct")
        for k in PROFILES:
            facts[f"{name}.flip_rate.{k}"] = _fact(res["by_profile"][k], "pct")
        facts[f"{name}.spread.median"] = _fact(res["spread"]["0.5"], "pct")
        facts[f"{name}.spread.p05"] = _fact(res["spread"]["0.05"], "pct")
        facts[f"{name}.spread.p95"] = _fact(res["spread"]["0.95"], "pct")
        for ax in AXES:
            facts[f"{name}.effect.{ax}"] = _fact(res["effects"][ax], "pct1")
    facts["top_axis_b"] = _fact(top, "str")
    facts.update({k: _fact(v["result"], "str") for k, v in preds.items()})
    return {"generator_a": a, "generator_b": b, "top_axis_b": top, "predictions": preds, "facts": facts}


# --------------------------------------------------------------------------- E3

PORTFOLIO_COLS = [(t, g) for t in (2, 3, 4) for g in ("none", "required")]
REFERENCE = (3, "none")
SCOPE = "all-services"


def competition_ranks(shares: dict[str, float]) -> dict[str, int]:
    """Rank 1 is the highest share; ties share the best rank (as in site/src/engine.ts)."""
    vals = sorted(shares.values(), reverse=True)
    return {k: vals.index(v) + 1 for k, v in shares.items()}


def _by_entity(items: list[ServiceItem]) -> dict[str, list[ServiceItem]]:
    out: dict[str, list[ServiceItem]] = {}
    for it in items:
        if in_scope(it, SCOPE):
            out.setdefault(it.entity_id, []).append(it)
    return out


def _shares(groups: dict[str, list[ServiceItem]], threshold: int, guard: str) -> dict[str, float]:
    return {e: sum(qualifies(i, threshold, guard) for i in g) / len(g) for e, g in groups.items()}


def _resample(groups, rng: random.Random):
    return {e: [g[rng.randrange(len(g))] for _ in g] for e, g in groups.items()}


def portfolio_table(reg: Registry) -> list[dict]:
    """Per entity: share and rank under each portfolio definition, as portfolio() in engine.ts."""
    groups = _by_entity(reg.items)
    shares = [_shares(groups, t, g) for t, g in PORTFOLIO_COLS]
    ranks = [competition_ranks(s) for s in shares]
    return [
        {"entity": e, "items": len(groups[e]),
         "shares": [s[e] for s in shares], "ranks": [r[e] for r in ranks]}
        for e in sorted(groups)
    ]


def rank_noise(reg: Registry, reps: int = 200, seed: int = 11, base_seed: int = 12) -> dict:
    groups = _by_entity(reg.items)
    ranks_by_def = [competition_ranks(_shares(groups, t, g)) for t, g in PORTFOLIO_COLS]
    def_range = {e: max(r[e] for r in ranks_by_def) - min(r[e] for r in ranks_by_def) for e in groups}
    rng = random.Random(seed)
    samples: dict[str, list[int]] = {e: [] for e in groups}
    for _ in range(reps):
        rk = competition_ranks(_shares(_resample(groups, rng), *REFERENCE))
        for e in groups:
            samples[e].append(rk[e])
    width = {e: quantile(samples[e], 0.95) - quantile(samples[e], 0.05) for e in groups}
    exceed = sorted(e for e in groups if def_range[e] > width[e])
    moved3 = sum(1 for e in groups if def_range[e] >= 3)
    rng_b = random.Random(base_seed)
    counts = []
    for _ in range(reps):
        sets = [competition_ranks(_shares(_resample(groups, rng_b), *REFERENCE)) for _ in range(6)]
        counts.append(sum(1 for e in groups if max(s[e] for s in sets) - min(s[e] for s in sets) > width[e]))
    return {
        "entities": len(groups),
        "moved_3_or_more": moved3,
        "exceed_noise": len(exceed),
        "exceed_ids": exceed,
        "noise_only_mean": round(statistics.mean(counts), 4),
        "definition_range": dict(sorted(def_range.items())),
        "noise_width": {e: round(w, 4) for e, w in sorted(width.items())},
    }


def e3() -> dict:
    import json

    from .io import ROOT

    reg = Registry.model_validate(
        json.loads((ROOT / "data" / "synthetic" / "registry.json").read_text(encoding="utf-8"))
    )
    primary = rank_noise(reg)
    seeds = [rank_noise(generate(seed=s, n_entities=16)) for s in range(1, 21)]
    ex = [s["exceed_noise"] for s in seeds]
    mv = [s["moved_3_or_more"] for s in seeds]
    preds = {
        "P3a": {
            "text": "entities exceeding noise between 3 and 9 on the committed registry",
            "result": _verdict(3 <= primary["exceed_noise"] <= 9),
        },
        "P3b": {
            "text": "fewer entities exceed noise than move by three places or more",
            "result": _verdict(primary["exceed_noise"] < primary["moved_3_or_more"]),
        },
        "P3c": {
            "text": "noise only baseline mean below 3",
            "result": _verdict(primary["noise_only_mean"] < 3),
        },
    }
    return {
        "primary": primary,
        "seeds": {
            "range": [1, 20],
            "exceed_noise": ex,
            "moved_3_or_more": mv,
            "exceed_mean": round(statistics.mean(ex), 4),
            "moved_mean": round(statistics.mean(mv), 4),
        },
        "predictions": preds,
        "facts": {
            "entities": _fact(primary["entities"], "int"),
            "moved3": _fact(primary["moved_3_or_more"], "int"),
            "exceed": _fact(primary["exceed_noise"], "int"),
            "noise_only_mean": _fact(primary["noise_only_mean"], "f2"),
            "seeds.exceed_mean": _fact(statistics.mean(ex), "f2"),
            "seeds.exceed_min": _fact(min(ex), "int"),
            "seeds.exceed_max": _fact(max(ex), "int"),
            "seeds.moved_mean": _fact(statistics.mean(mv), "f2"),
            **{k: _fact(v["result"], "str") for k, v in preds.items()},
        },
    }


# --------------------------------------------------------------------------- E4


def percentile_boot(k: int, n: int, rng: random.Random, reps: int = 2000) -> tuple[float, float]:
    p = k / n
    vals = [rng.binomialvariate(n, p) / n for _ in range(reps)]
    return quantile(vals, 0.025), quantile(vals, 0.975)


def coverage(rate: float, n: int = 25, seeds: range = range(1, 21), runs: int = 100) -> dict:
    per_seed: dict[str, list[float]] = {"bootstrap": [], "wilson": []}
    widths: dict[str, list[float]] = {"bootstrap": [], "wilson": []}
    for seed in seeds:
        rng = random.Random(seed)
        hits = {"bootstrap": 0, "wilson": 0}
        for _ in range(runs):
            k = sum(rng.random() < rate for _ in range(n))
            for name, (lo, hi) in (("bootstrap", percentile_boot(k, n, rng)), ("wilson", wilson(k, n))):
                hits[name] += lo <= rate <= hi
                widths[name].append(hi - lo)
        for name in hits:
            per_seed[name].append(hits[name] / runs)
    out = {}
    for name, xs in per_seed.items():
        m = statistics.mean(xs)
        se = statistics.stdev(xs) / math.sqrt(len(xs))
        out[name] = {
            "coverage": round(m, 4),
            "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)],
            "mean_width": round(statistics.mean(widths[name]), 4),
        }
    return out


RATES = (0.70, 0.88, 0.95)


def e4() -> dict:
    res = {f"{r:.2f}": coverage(r) for r in RATES}
    b = {k: v["bootstrap"]["coverage"] for k, v in res.items()}
    w = {k: v["wilson"]["coverage"] for k, v in res.items()}
    preds = {
        "P4a": {
            "text": "bootstrap coverage at 0.70 between 0.90 and 0.95",
            "result": _verdict(0.90 <= b["0.70"] <= 0.95),
        },
        "P4b": {
            "text": "bootstrap coverage at 0.88 between 0.85 and 0.93",
            "result": _verdict(0.85 <= b["0.88"] <= 0.93),
        },
        "P4c": {"text": "bootstrap coverage at 0.95 below 0.85", "result": _verdict(b["0.95"] < 0.85)},
        "P4d": {
            "text": "Wilson coverage at least 0.92 at all three rates",
            "result": _verdict(min(w.values()) >= 0.92),
        },
    }
    facts = {}
    for k, v in res.items():
        key = k.replace("0.", "p")
        for name in ("bootstrap", "wilson"):
            facts[f"{key}.{name}"] = _fact(v[name]["coverage"], "pct1")
            facts[f"{key}.{name}.width"] = _fact(v[name]["mean_width"], "f2")
    facts.update({k: _fact(v["result"], "str") for k, v in preds.items()})
    return {
        "n": 25,
        "runs_per_rate": 2000,
        "resamples": 2000,
        "rates": res,
        "predictions": preds,
        "facts": facts,
    }


EXPERIMENTS = {"e1": e1, "e2": e2, "e3": e3, "e4": e4, "e5": e5, "e6": e6}
