"""Agreement between the ledger and the blind second extraction, with bootstrap intervals.

Matching rule (fixed in code so it can be rerun): a blind item matches a ledger commitment when they
share at least one source id AND (both carry the same number, or their titles share >= 35% of words).
"""

from __future__ import annotations

import json
import re

from .io import REAL
from .schemas import Commitment
from .stats import bootstrap_ci

_STOP = {"the", "a", "of", "and", "to", "in", "for", "on", "by", "with", "all", "across", "ai", "uae"}


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in _STOP and len(w) > 2}


def matches(c: Commitment, b: dict) -> bool:
    if not set(c.source_ids) & set(b.get("sources") or []):
        return False
    if c.target_number is not None and b.get("number") is not None and float(b["number"]) == c.target_number:
        return True
    a, w = words(c.title + " " + c.statement), words(b["title"])
    return bool(w) and len(a & w) / len(w) >= 0.35


def run(cs: list[Commitment]) -> dict:
    blind = json.loads((REAL / "blind_extraction.json").read_text(encoding="utf-8"))["commitments"]
    hit = [any(matches(c, b) for b in blind) for c in cs]
    numeric = [c for c in cs if c.target_number is not None]
    nhit = [any(matches(c, b) and b.get("number") is not None for b in blind) for c in numeric]

    def rate(xs):
        return lambda ix: sum(xs[i] for i in ix) / len(ix)

    return {
        "ledger_commitments": len(cs),
        "blind_items": len(blind),
        "recall": {"found": sum(hit), "n": len(hit), "rate": round(sum(hit) / len(hit), 3),
                   "ci95": bootstrap_ci(len(hit), rate(hit))},
        "numeric_recall": {"found": sum(nhit), "n": len(nhit), "rate": round(sum(nhit) / len(nhit), 3),
                           "ci95": bootstrap_ci(len(nhit), rate(nhit))},
        "missed": [c.id for c, h in zip(cs, hit, strict=True) if not h],
        "note": (
            "The blind pass read the same extraction notes, so this measures consistency of reading, not "
            "faithfulness to the web pages. Precision is not reported: the blind pass counted reported "
            "achievements as commitments by design."
        ),
    }
