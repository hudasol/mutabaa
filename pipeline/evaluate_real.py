"""Preregistered experiments E5 and E6 on the real ledger (see PREREGISTRATION.md, part two).

E5 compares plain rule based extractors with the curated ledger. E6 checks the status engine against
its stated invariants and checks that the invariants would notice five deliberately broken engines.
No synthetic data and no language model are used. Perturbations in E6 exist in memory only.
"""

from __future__ import annotations

import json
import random
import re
import statistics
from collections.abc import Callable
from contextlib import AbstractContextManager, contextmanager
from datetime import date, timedelta

from . import status as status_module
from .io import ROOT, load_real
from .schemas import Commitment, Evidence, EvidenceKind, Source, StatusResult

ANALYSIS = ROOT / "data" / "analysis"


def _fact(value, fmt: str) -> dict:
    return {"value": value, "format": fmt}


def _verdict(ok: bool) -> str:
    return "HIT" if ok else "MISS"


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


# --------------------------------------------------------------------------- E5


def note_units(text: str) -> list[str]:
    """Bullets of an extraction note: a `- ` line plus indented continuation lines, at least four words."""
    units: list[str] = []
    current: list[str] | None = None
    for line in text.splitlines():
        if line.startswith("- "):
            if current is not None:
                units.append(" ".join(current))
            current = [line[2:].strip()]
        elif current is not None and line[:1] in (" ", "\t") and line.strip():
            current.append(line.strip())
        else:
            if current is not None:
                units.append(" ".join(current))
            current = None
    if current is not None:
        units.append(" ".join(current))
    return [u for u in units if len(u.split()) >= 4]


_DIGIT = re.compile(r"[0-9٠-٩]")
_MARKER = re.compile(r"\b(percent|aed|billion|million|trillion)\b")
_YEAR = re.compile(r"\b20(2[4-9]|3[0-5])\b")
_CUE = re.compile(r"\b(will|target|aim|plan|launch|transform|establish|commit)\b")


def x0(t: str) -> bool:
    return True


def x1(t: str) -> bool:
    return bool(_DIGIT.search(t))


def x2(t: str) -> bool:
    return x1(t) and ("%" in t or bool(_MARKER.search(t)))


def x3(t: str) -> bool:
    return x2(t) and (bool(_YEAR.search(t)) or "within" in t or "by end of" in t)


def x4(t: str) -> bool:
    return bool(_CUE.search(t))


EXTRACTORS: dict[str, Callable[[str], bool]] = {"x0": x0, "x1": x1, "x2": x2, "x3": x3, "x4": x4}


def _f1(p: float | None, r: float) -> float:
    return 0.0 if not p or not r else 2 * p * r / (p + r)


def e5() -> dict:
    d = load_real()
    units: dict[tuple[str, int], str] = {}
    for s in d.sources:
        text = (ROOT / s.extract_file).read_text(encoding="utf-8")
        for i, u in enumerate(note_units(text)):
            units[(s.id, i)] = _norm(u)

    evidence_units: dict[str, set[tuple[str, int]]] = {}
    for c in d.commitments:
        hits: set[tuple[str, int]] = set()
        for a in c.anchors:
            needle = _norm(a.text)
            hits |= {k for k, u in units.items() if k[0] == a.source_id and needle in u}
        evidence_units[c.id] = hits
    located = [c for c in d.commitments if evidence_units[c.id]]
    unlocated = [c.id for c in d.commitments if not evidence_units[c.id]]
    positives = set().union(*evidence_units.values())
    numeric = [c for c in located if c.target_number is not None]
    other = [c for c in located if c.target_number is None]

    def recall(flagged: set, group: list[Commitment]) -> float:
        return sum(bool(evidence_units[c.id] & flagged) for c in group) / len(group)

    rows: dict[str, dict] = {}
    for name, fn in EXTRACTORS.items():
        flagged = {k for k, u in units.items() if fn(u)}
        hit = flagged & positives
        prec = len(hit) / len(flagged) if flagged else None
        urec = len(hit) / len(positives)
        rows[name] = {
            "flagged": len(flagged),
            "flagged_share": round(len(flagged) / len(units), 4),
            "recall": recall(flagged, located),
            "recall_numeric": recall(flagged, numeric) if numeric else None,
            "recall_other": recall(flagged, other) if other else None,
            "unit_recall": round(urec, 4),
            "precision": None if prec is None else round(prec, 4),
            "f1": round(_f1(prec, urec), 4),
        }

    p_x2 = rows["x2"]["flagged_share"]
    keys = sorted(units)
    random_recalls = []
    for seed in range(1, 21):
        rng = random.Random(seed)
        flagged = {k for k in keys if rng.random() < p_x2}
        random_recalls.append(recall(flagged, located))
    random_mean = statistics.mean(random_recalls)

    # Exploratory, added after the results existed (amendment 5): the same random baseline, but flagging
    # each unit with the extractor's own flag share, so recall is compared at equal effort.
    matched: dict[str, float] = {}
    for name in ("x1", "x2", "x3", "x4"):
        share = rows[name]["flagged_share"]
        vals = []
        for seed in range(1, 21):
            rng = random.Random(seed)
            vals.append(recall({k for k in keys if rng.random() < share}, located))
        matched[name] = statistics.mean(vals)

    blind = json.loads((ANALYSIS / "agreement.json").read_text(encoding="utf-8"))["recall"]
    blind_rate = blind["found"] / blind["n"]

    best_f1 = max(rows[k]["f1"] for k in ("x1", "x2", "x3", "x4"))
    preds = {
        "P5a": {
            "text": "X2 recovers at least 0.70 of numeric target commitments and at most 0.50 of the others",
            "result": _verdict(rows["x2"]["recall_numeric"] >= 0.70 and rows["x2"]["recall_other"] <= 0.50),
        },
        "P5b": {
            "text": "no extractor from X1 to X4 has unit F1 above 0.45",
            "result": _verdict(best_f1 <= 0.45),
        },
        "P5c": {"text": "X1 unit precision below 0.50", "result": _verdict(rows["x1"]["precision"] < 0.50)},
        "P5d": {
            "text": "blind second reading recall above X3, and X3 above the random baseline mean",
            "result": _verdict(blind_rate > rows["x3"]["recall"] > random_mean),
        },
        "P5e": {"text": "no unlocated commitments", "result": _verdict(not unlocated)},
    }
    facts = {
        "units": _fact(len(units), "int"),
        "positives": _fact(len(positives), "int"),
        "located": _fact(len(located), "int"),
        "unlocated": _fact(len(unlocated), "int"),
        "numeric": _fact(len(numeric), "int"),
        "other": _fact(len(other), "int"),
        "random.mean": _fact(random_mean, "pct"),
        "blind.recall": _fact(blind_rate, "pct"),
        "best_f1": _fact(best_f1, "f2"),
    }
    for name, r in rows.items():
        facts[f"{name}.flagged_share"] = _fact(r["flagged_share"], "pct")
        facts[f"{name}.recall"] = _fact(r["recall"], "pct")
        facts[f"{name}.recall_numeric"] = _fact(r["recall_numeric"], "pct")
        facts[f"{name}.recall_other"] = _fact(r["recall_other"], "pct")
        facts[f"{name}.precision"] = _fact(r["precision"], "pct")
        facts[f"{name}.f1"] = _fact(r["f1"], "f2")
        if name in matched:
            facts[f"{name}.random_matched"] = _fact(matched[name], "pct")
    facts.update({k: _fact(v["result"], "str") for k, v in preds.items()})
    return {
        "extractors": rows,
        "random_recalls": random_recalls,
        "random_matched_exploratory": matched,
        "unlocated_ids": unlocated,
        "predictions": preds,
        "facts": facts,
    }


# --------------------------------------------------------------------------- E6

# The oracle below states the rules independently of pipeline.status, so a patched engine cannot change it.
NON_OUTCOME = ("vision", "projection", "assessment")
STALE_DAYS = 180


def oracle_eligible(e: Evidence, sources: dict[str, Source]) -> bool:
    return sources[e.source_id].kind != "secondary-media" or e.corroboration == "official-confirmed"


ORDER = {"no-public-evidence": 0, "activity-reported": 1, "milestone-reported": 2, "target-claimed-met": 3}
StatusFn = Callable[[Commitment, list[Evidence], dict[str, Source], date], StatusResult]


def _ev(i: int, c: Commitment, source: Source, kind: EvidenceKind, as_of: date, **kw) -> Evidence:
    return Evidence(
        id=f"E{90 + i}",
        commitment_ids=[c.id],
        kind=kind,
        summary="perturbation",
        summary_ar="perturbation",
        as_of=as_of,
        source_id=source.id,
        anchor="perturbation",
        **kw,
    )


def _core(r: StatusResult) -> tuple:
    """What a result means, with evidence ids as a set (their order follows the input order)."""
    return (
        r.status,
        r.progress_ratio,
        r.progress_as_of,
        r.stale,
        r.unit_mismatch,
        r.self_reported_only,
        frozenset(r.evidence_ids),
    )


def check_invariants(fn: StatusFn, d, as_of: date) -> dict[str, list[str]]:
    """Violations per invariant, as lists of commitment ids."""
    src = {s.id: s for s in d.sources}
    media = next(s for s in d.sources if s.kind == "secondary-media")
    official = next(s for s in d.sources if s.kind in ("official-statement", "official-self-report"))
    bad: dict[str, list[str]] = {k: [] for k in ("I1", "I2", "I3", "I4", "I5")}
    for c in d.commitments:
        mine = [e for e in d.evidence if c.id in e.commitment_ids]
        base = fn(c, d.evidence, src, as_of)

        none = fn(c, [], src, as_of)
        want = "not-checkable" if c.kind in NON_OUTCOME else "no-public-evidence"
        if none.status != want:
            bad["I1"].append(c.id)

        m = _ev(1, c, media, "quantified-progress", as_of, corroboration="single-source",
                value=c.target_number or 1.0, unit=c.unit)
        with_media = fn(c, [*d.evidence, m], src, as_of)
        if (with_media.status, with_media.evidence_ids, with_media.progress_ratio) != (
            base.status, base.evidence_ids, base.progress_ratio,
        ):
            bad["I2"].append(c.id)

        for seed in range(1, 21):
            shuffled = list(d.evidence)
            random.Random(seed).shuffle(shuffled)
            if _core(fn(c, shuffled, src, as_of)) != _core(base):
                bad["I3"].append(c.id)
                break

        variants: list[list[Evidence]] = [[_ev(2, c, official, "activity", as_of)]]
        if c.unit and c.target_number:
            variants.append([_ev(3, c, official, "quantified-progress", as_of,
                                 value=c.target_number / 2, unit=c.unit)])
            variants.append([_ev(4, c, official, "quantified-progress", as_of,
                                 value=c.target_number, unit=c.unit),
                             _ev(5, c, official, "target-met-claim", as_of)])
        else:
            variants.append([_ev(5, c, official, "target-met-claim", as_of)])
        for extra in variants:
            after = fn(c, [*d.evidence, *extra], src, as_of)
            if base.status == "not-checkable":
                ok = after.status == "not-checkable"
            else:
                ok = after.status != "not-checkable" and ORDER[after.status] >= ORDER[base.status]
            if not ok:
                bad["I4"].append(c.id)
                break

        dated = [e.as_of for e in mine if e.as_of and oracle_eligible(e, src)]
        latest = max(dated) if dated else None
        for delta in (-400, -1, 0, 1, 181, 400):
            when = as_of + timedelta(days=delta)
            r = fn(c, d.evidence, src, when)
            expect = latest is not None and (when - latest).days > STALE_DAYS
            if r.status != base.status or r.stale != expect:
                bad["I5"].append(c.id)
                break
    return bad


@contextmanager
def _patched(**attrs):
    old = {k: getattr(status_module, k) for k in attrs}
    for k, v in attrs.items():
        setattr(status_module, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(status_module, k, v)


def mutant_fns() -> dict[str, tuple[str, Callable[[], AbstractContextManager[None]]]]:
    """Name -> (description, context manager factory) for five altered copies of the engine."""
    real = status_module.status

    def m2(c, evidence, sources, data_as_of=None):
        keep = [
            e for e in evidence
            if not (data_as_of and e.as_of and (data_as_of - e.as_of).days > status_module.STALE_AFTER_DAYS)
        ]
        return real(c, keep, sources, data_as_of)

    def m3(c, evidence, sources, data_as_of=None):
        first = next((e for e in evidence if c.id in e.commitment_ids), None)
        return real(c, [first] if first else [], sources, data_as_of)

    def m4(c, evidence, sources, data_as_of=None):
        r = real(c, evidence, sources, data_as_of)
        return r.model_copy(update={"status": "not-checkable"}) if r.status == "no-public-evidence" else r

    def m5(c, evidence, sources, data_as_of=None):
        if c.kind in status_module.NON_OUTCOME_KINDS:
            return real(c.model_copy(update={"kind": "deliverable"}), evidence, sources, data_as_of)
        return real(c, evidence, sources, data_as_of)

    return {
        "M1": ("media evidence counts as eligible", lambda: _patched(eligible=lambda e, s: True)),
        "M2": ("evidence older than 180 days is dropped", lambda: _patched(status=m2)),
        "M3": ("only the first evidence item is used", lambda: _patched(status=m3)),
        "M4": ("no evidence gives not-checkable for every kind", lambda: _patched(status=m4)),
        "M5": ("the non outcome rule runs after the evidence rules", lambda: _patched(status=m5)),
    }


def e6() -> dict:
    d = load_real()
    as_of = max(s.retrieved for s in d.sources)
    src = {s.id: s for s in d.sources}

    def real_fn(c, ev, s, when):
        return status_module.status(c, ev, s, when)

    def live_fn(c, ev, s, when):  # looks the engine up at call time so patches take effect
        return status_module.status(c, ev, s, when)

    real = check_invariants(real_fn, d, as_of)
    killed: dict[str, list[str]] = {}
    for name, (_, patch) in mutant_fns().items():
        with patch():
            res = check_invariants(live_fn, d, as_of)
        killed[name] = [k for k, v in res.items() if v]
    multi = sum(
        sum(1 for e in d.evidence if c.id in e.commitment_ids and oracle_eligible(e, src)) >= 2
        for c in d.commitments
    )
    n_killed = sum(bool(v) for v in killed.values())
    preds = {
        "P6a": {
            "text": "zero violations of every invariant on the real engine",
            "result": _verdict(not any(real.values())),
        },
        "P6b": {"text": "at least four of the five mutants are killed", "result": _verdict(n_killed >= 4)},
        "P6c": {
            "text": "at most three commitments have two or more eligible evidence items",
            "result": _verdict(multi <= 3),
        },
    }
    facts = {
        "commitments": _fact(len(d.commitments), "int"),
        "multi_evidence": _fact(multi, "int"),
        "mutants": _fact(len(killed), "int"),
        "killed": _fact(n_killed, "int"),
        "violations": _fact(sum(len(v) for v in real.values()), "int"),
        **{f"violations.{k}": _fact(len(v), "int") for k, v in real.items()},
        **{f"mutant.{k}": _fact(", ".join(v) if v else "none", "str") for k, v in killed.items()},
    }
    facts.update({k: _fact(v["result"], "str") for k, v in preds.items()})
    return {
        "violations": real,
        "mutants": {k: {"describe": mutant_fns()[k][0], "violated": v} for k, v in killed.items()},
        "predictions": preds,
        "facts": facts,
    }
