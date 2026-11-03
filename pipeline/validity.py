"""E8: does the verifiability score predict a later public report on the stated measure?

Step A (`freeze`) writes the score and two trivial baselines for every commitment with a deadline before the
cutoff. It runs before any outcome is searched. Step C (`e8`) reads the frozen file, the outcomes and the
search log, and tests the score. The design is in PREREGISTRATION.md, section E8.
"""

from __future__ import annotations

import json
import random
import re
from datetime import date

from .evaluate_real import _fact, _verdict
from .io import ROOT, load_real
from .score import score

E8_DIR = ROOT / "data" / "e8"
CUTOFF = date(2026, 6, 30)
RETRIEVAL_LIMIT = date(2026, 11, 3)
PERMUTATIONS = 10000
PERMUTATION_SEED = 1


def population() -> list[str]:
    """Commitments whose deadline is before the cutoff, in identifier order."""
    d = load_real()
    return sorted(c.id for c in d.commitments if c.deadline is not None and c.deadline < CUTOFF)


def freeze() -> dict:
    """Score, statement length and digit presence for each commitment in the population."""
    d = load_real()
    by_id = {c.id: c for c in d.commitments}
    rows = {}
    for cid in population():
        c = by_id[cid]
        s = score(c)
        rows[cid] = {
            "score": s.ratio,
            "band": s.band,
            "statement_length": len(c.statement),
            "has_digit": bool(re.search(r"\d", c.statement)),
            "deadline": c.deadline.isoformat() if c.deadline else None,
        }
    return {
        "design": "PREREGISTRATION.md, section E8, step A",
        "cutoff": CUTOFF.isoformat(),
        "n": len(rows),
        "commitments": rows,
    }


def _auc_tools():
    """The AUC helpers live in evaluate.py, which imports this module; look them up at call time."""
    from .evaluate import auc, auc_ci, auc_required

    return auc, auc_ci, auc_required


def permutation_p(scores: list[float], labels: list[bool], observed: float) -> float:
    """One sided: share of shuffles with an AUC at least as large, counting the observed one."""
    _, _, auc_required = _auc_tools()
    rng = random.Random(PERMUTATION_SEED)
    shuffled = list(labels)
    hits = 1
    for _ in range(PERMUTATIONS):
        rng.shuffle(shuffled)
        v = auc_required(scores, shuffled)
        if v >= observed - 1e-12:
            hits += 1
    return hits / (PERMUTATIONS + 1)


def e8() -> dict:
    auc, auc_ci, auc_required = _auc_tools()
    frozen = json.loads((E8_DIR / "frozen_scores.json").read_text(encoding="utf-8"))
    outcomes = json.loads((E8_DIR / "outcomes.json").read_text(encoding="utf-8"))["outcomes"]
    ids = sorted(frozen["commitments"])
    if sorted(outcomes) != ids:
        raise ValueError("outcomes must cover exactly the frozen population")
    rows = frozen["commitments"]
    y = [outcomes[i]["found"] for i in ids]
    s = [rows[i]["score"] for i in ids]
    length = [float(rows[i]["statement_length"]) for i in ids]
    digit = [float(rows[i]["has_digit"]) for i in ids]
    n_pos = sum(y)
    n_neg = len(y) - n_pos
    point = auc(s, y)
    result: dict = {"n": len(ids), "positives": n_pos, "negatives": n_neg}
    facts = {
        "n": _fact(len(ids), "int"),
        "positives": _fact(n_pos, "int"),
        "negatives": _fact(n_neg, "int"),
    }
    if point is None:
        result.update({"auc": None, "predictions": {}, "facts": facts})
        result["note"] = "only one outcome class: no AUC"
        return result
    lo, hi = auc_ci(s, y)
    p = permutation_p(s, y, point)
    base = {"statement_length": auc_required(length, y), "has_digit": auc_required(digit, y)}
    best = max(base.values())
    preds = {
        "P8a": {"text": "score AUC at least 0.55", "result": _verdict(point >= 0.55)},
        "P8b": {"text": "one sided permutation p at least 0.05", "result": _verdict(p >= 0.05)},
        "P8c": {
            "text": "score AUC at least the better baseline minus 0.05",
            "result": _verdict(point >= best - 0.05),
        },
        "P8d": {
            "text": "between 10% and 40% of the population has outcome 1",
            "result": _verdict(0.10 <= n_pos / len(ids) <= 0.40),
        },
        "P8e": {
            "text": "score AUC above statement length AUC",
            "result": _verdict(point > base["statement_length"]),
        },
    }
    facts.update(
        {
            "auc": _fact(point, "f2"),
            "ci_low": _fact(lo, "f2"),
            "ci_high": _fact(hi, "f2"),
            "p": _fact(p, "f3"),
            "baseline.length": _fact(base["statement_length"], "f2"),
            "baseline.digit": _fact(base["has_digit"], "f2"),
            "share": _fact(n_pos / len(ids), "pct"),
        }
    )
    facts.update({k: _fact(v["result"], "str") for k, v in preds.items()})
    result.update(
        {
            "auc": round(point, 4),
            "ci95": [round(lo, 4), round(hi, 4)],
            "permutation_p": round(p, 4),
            "baselines": {k: round(v, 4) for k, v in base.items()},
            "enough_per_class": n_pos >= 5 and n_neg >= 5,
            "predictions": preds,
            "facts": facts,
        }
    )
    return result
