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
from .io import ROOT, RealData, load_real
from .lint import lint
from .schemas import Commitment, Evidence, EvidenceKind, Source, StatusResult
from .score import score
from .stats import spearman

ANALYSIS = ROOT / "data" / "analysis"
FIRST_COHORT_LAST = 25
FIRST_SOURCE_LAST = 14


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


def registered() -> RealData:
    """The ledger as it stood when E5 and E6 were registered (v1.6.0): C01 to C25 and S01 to S14.

    The ledger grew in v1.7.0. The two experiments keep their registered scope so that their results do not
    change when records are added.
    """
    d = load_real()
    ids = {c.id for c in d.commitments if int(c.id[1:]) <= 25}
    return RealData(
        sources=[s for s in d.sources if int(s.id[1:]) <= 14],
        commitments=[c for c in d.commitments if c.id in ids],
        evidence=[e for e in d.evidence if set(e.commitment_ids) <= ids],
        claims=[k for k in d.claims if set(k.commitment_ids) <= ids],
        searches=[q for q in d.searches if set(q.commitment_ids) <= ids],
        verification=d.verification,
    )


def e5() -> dict:
    d = registered()
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

    blind = json.loads((ANALYSIS / "agreement.json").read_text(encoding="utf-8"))["first_cohort"]["recall"]
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
    d = registered()
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


def e7() -> dict:
    """E7: the blind second reading and the live verifier on the commitments and sources added in v1.7.0.

    Reads `data/analysis/agreement.json`, `data/analysis/verify_first_run.json` (the first run of the live
    verifier over the new sources, kept as recorded) and the score of each new commitment.
    """
    ag = json.loads((ANALYSIS / "agreement.json").read_text(encoding="utf-8"))
    first_run = json.loads((ANALYSIS / "verify_first_run.json").read_text(encoding="utf-8"))
    d = load_real()
    new = [c for c in d.commitments if int(c.id[1:]) > FIRST_COHORT_LAST]
    bands = [score(c).band for c in new]
    checkable = sum(b == "checkable" for b in bands)
    now = d.verification["results"]
    new_ids = {s.id for s in d.sources if int(s.id[1:]) > FIRST_SOURCE_LAST}
    verified_first = sum(first_run[i]["result"] == "verified" for i in new_ids)
    verified_now = sum(now[i]["result"] == "verified" for i in new_ids)
    nc, fc = ag["new_cohort"], ag["first_cohort"]
    preds = {
        "P7a": {
            "text": "recall on the new commitments is at least 75%",
            "result": _verdict(nc["recall"]["rate"] >= 0.75),
        },
        "P7b": {
            "text": "numeric recall on the new commitments is at least 75%",
            "result": _verdict(nc["numeric_recall"]["rate"] >= 0.75),
        },
        "P7c": {
            "text": "recall on the new commitments is lower than 88%",
            "result": _verdict(nc["recall"]["rate"] < 0.88),
        },
        "P7d": {
            "text": "at least 60% of the new sources are verified on the first run of verify-live",
            "result": _verdict(verified_first / len(new_ids) >= 0.60),
        },
        "P7e": {
            "text": "at most 15% of the new commitments reach the band checkable",
            "result": _verdict(checkable / len(new) <= 0.15),
        },
    }
    facts = {
        "new.commitments": _fact(len(new), "int"),
        "new.sources": _fact(len(new_ids), "int"),
        "new.recall": _fact(nc["recall"]["rate"], "pct"),
        "new.recall.found": _fact(nc["recall"]["found"], "int"),
        "new.recall.ci_low": _fact(nc["recall"]["wilson95"][0], "pct"),
        "new.recall.ci_high": _fact(nc["recall"]["wilson95"][1], "pct"),
        "new.numeric": _fact(nc["numeric_recall"]["rate"], "pct"),
        "new.numeric.found": _fact(nc["numeric_recall"]["found"], "int"),
        "new.numeric.n": _fact(nc["numeric_recall"]["n"], "int"),
        "first.recall": _fact(fc["recall"]["rate"], "pct"),
        "verified.first": _fact(verified_first, "int"),
        "verified.first.share": _fact(verified_first / len(new_ids), "pct"),
        "verified.now": _fact(verified_now, "int"),
        "checkable": _fact(checkable, "int"),
        "checkable.share": _fact(checkable / len(new), "pct"),
    }
    facts.update({k: _fact(v["result"], "str") for k, v in preds.items()})
    return {
        "first_run_unverified": {
            i: first_run[i]["result"] for i in sorted(new_ids) if first_run[i]["result"] != "verified"
        },
        "band_counts": {b: bands.count(b) for b in ("checkable", "partly-checkable", "not-yet-checkable")},
        "predictions": preds,
        "facts": facts,
    }


def _f1_counts(tp: int, fp: int, fn: int) -> float:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return 0.0 if not p or not r else 2 * p * r / (p + r)


def e9() -> dict:
    """E9: the linter, reading only the English statement, against the curated fields (all commitments)."""
    d = load_real()
    rows = []
    for c in d.commitments:
        r = lint(c.statement)
        f = r["found"]
        s = score(c)
        year_c = c.deadline.year if c.deadline and c.deadline_precision in ("day", "month", "year") else None
        m = re.search(r"(?:19|20)\d{2}", f["deadline_text"] or "")
        rows.append(
            {
                "id": c.id,
                "num_c": c.target_number is not None,
                "num_l": f["target_number"] is not None,
                "num_equal": c.target_number is not None
                and f["target_number"] is not None
                and abs(c.target_number - f["target_number"]) < 1e-9,
                "digit": bool(re.search(r"\d", c.statement)),
                "year_c": year_c,
                "year_l": int(m.group(0)) if m else None,
                "own_c": c.owner is not None,
                "own_l": f["owner"] is not None,
                "src_c": c.measurement_source is not None,
                "src_l": f["measurement_source"] is not None,
                "ratio_c": s.ratio,
                "ratio_l": r["before"]["ratio"],
                "band_c": s.band,
                "band_l": r["before"]["band"],
            }
        )
    n = len(rows)
    tp = sum(x["num_c"] and x["num_l"] for x in rows)
    fp = sum(not x["num_c"] and x["num_l"] for x in rows)
    fn = sum(x["num_c"] and not x["num_l"] for x in rows)
    f1 = _f1_counts(tp, fp, fn)
    dtp = sum(x["num_c"] and x["digit"] for x in rows)
    dfp = sum(not x["num_c"] and x["digit"] for x in rows)
    dfn = sum(x["num_c"] and not x["digit"] for x in rows)
    f1_digit = _f1_counts(dtp, dfp, dfn)
    both = [x for x in rows if x["num_c"] and x["num_l"]]
    value_agree = sum(x["num_equal"] for x in both) / len(both) if both else 0.0
    dated = [x for x in rows if x["year_c"] is not None]
    year_agree = sum(x["year_l"] == x["year_c"] for x in dated) / len(dated) if dated else 0.0
    own_acc = sum(x["own_c"] == x["own_l"] for x in rows) / n
    own_base = max(sum(x["own_c"] for x in rows), n - sum(x["own_c"] for x in rows)) / n
    rho = spearman([x["ratio_l"] for x in rows], [x["ratio_c"] for x in rows])
    band_agree = sum(x["band_c"] == x["band_l"] for x in rows) / n
    src_tp = sum(x["src_c"] and x["src_l"] for x in rows)
    src_fp = sum(not x["src_c"] and x["src_l"] for x in rows)
    src_fn = sum(x["src_c"] and not x["src_l"] for x in rows)
    preds = {
        "P9a": {"text": "number presence F1 at least 0.85", "result": _verdict(f1 >= 0.85)},
        "P9b": {"text": "number value agreement at least 0.80", "result": _verdict(value_agree >= 0.80)},
        "P9c": {"text": "deadline year agreement at least 0.80", "result": _verdict(year_agree >= 0.80)},
        "P9d": {"text": "owner presence accuracy at least 0.70", "result": _verdict(own_acc >= 0.70)},
        "P9e": {"text": "Spearman of the two ratios at least 0.60", "result": _verdict((rho or 0.0) >= 0.60)},
        "P9f": {"text": "exact band agreement at least 0.60", "result": _verdict(band_agree >= 0.60)},
        "P9g": {"text": "number presence F1 above the digit baseline", "result": _verdict(f1 > f1_digit)},
    }
    facts = {
        "n": _fact(n, "int"),
        "number.f1": _fact(f1, "f2"),
        "number.precision": _fact(tp / (tp + fp) if tp + fp else 0.0, "f2"),
        "number.recall": _fact(tp / (tp + fn) if tp + fn else 0.0, "f2"),
        "number.digit_f1": _fact(f1_digit, "f2"),
        "number.value": _fact(value_agree, "f2"),
        "number.both": _fact(len(both), "int"),
        "year": _fact(year_agree, "f2"),
        "year.n": _fact(len(dated), "int"),
        "owner": _fact(own_acc, "f2"),
        "owner.baseline": _fact(own_base, "f2"),
        "rho": _fact(rho, "f2"),
        "band": _fact(band_agree, "f2"),
        "source.tp": _fact(src_tp, "int"),
        "source.fp": _fact(src_fp, "int"),
        "source.fn": _fact(src_fn, "int"),
    }
    facts.update({k: _fact(v["result"], "str") for k, v in preds.items()})
    disagree = {k: [x["id"] for x in rows if not v(x)] for k, v in {
        "number_presence": lambda x: x["num_c"] == x["num_l"],
        "owner_presence": lambda x: x["own_c"] == x["own_l"],
        "band": lambda x: x["band_c"] == x["band_l"],
    }.items()}
    return {"disagreements": disagree, "predictions": preds, "facts": facts}
