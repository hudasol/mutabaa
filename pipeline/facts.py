"""Facts that documents are allowed to cite, computed from files the code produces.

`python -m pipeline facts` writes results/facts.json. Each fact has a raw value and the text a document
must show. Documents wrap a cited number as <!-- fact:KEY -->TEXT<!-- /fact -->, and
tests/test_docs_agree.py fails when TEXT differs from the fact or the fact differs from a fresh computation.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .io import ROOT

PAYLOAD = ROOT / "site" / "src" / "data" / "real.json"
ANALYSIS = ROOT / "data" / "analysis"
RESULTS = ROOT / "results"


def fmt(value, kind: str) -> str:
    if kind == "int":
        return f"{int(value):,}"
    if kind == "pct":
        return f"{round(value * 100):d}%"
    if kind == "pct1":
        return f"{value * 100:.1f}%"
    if kind == "f2":
        return f"{value:.2f}"
    if kind == "f3":
        return f"{value:.3f}"
    if kind == "str":
        return str(value)
    if kind == "list":
        return ", ".join(value)
    raise ValueError(f"unknown format {kind!r}")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluation() -> dict:
    """Preregistered evaluation results, if `python -m pipeline evaluate` has been run."""
    out = {}
    if RESULTS.exists():
        for p in sorted(RESULTS.glob("e*.json")):
            out[p.stem] = _load(p)
    return out


def raw_facts() -> dict[str, tuple[object, str]]:
    """Key -> (value, format). Keep keys stable: documents refer to them."""
    p = _load(PAYLOAD)
    rb = _load(ANALYSIS / "robustness.json")
    cal = _load(ANALYSIS / "calibration.json")
    ag = _load(ANALYSIS / "agreement.json")
    f: dict[str, tuple[object, str]] = {}

    kinds = Counter(s["kind"] for s in p["sources"])
    ver = Counter(v["result"] for v in p["verification"]["results"].values())
    f["sources.count"] = (len(p["sources"]), "int")
    f["sources.official"] = (kinds["official-statement"] + kinds["official-self-report"], "int")
    f["sources.official_statement"] = (kinds["official-statement"], "int")
    f["sources.official_self_report"] = (kinds["official-self-report"], "int")
    f["sources.media"] = (kinds["secondary-media"], "int")
    f["sources.verified"] = (ver["verified"], "int")
    f["sources.unreachable"] = (ver["unreachable"], "int")
    f["commitments.count"] = (len(p["commitments"]), "int")
    f["evidence.count"] = (len(p["evidence"]), "int")
    f["claims.count"] = (len(p["claims"]), "int")
    f["searches.count"] = (len(p["searches"]), "int")
    bands = Counter(s["band"] for s in p["scores"])
    f["bands.fully"] = (bands["checkable"], "int")
    f["bands.partly"] = (bands["partly-checkable"], "int")
    f["bands.under"] = (bands["not-yet-checkable"], "int")
    st = Counter(s["status"] for s in p["statuses"])
    for k in ("not-checkable", "no-public-evidence", "activity-reported",
              "milestone-reported", "target-claimed-met"):
        f[f"status.{k}"] = (st[k], "int")
    f["registry.entities"] = (len(p["synthetic"]["entities"]), "int")
    f["registry.items"] = (len(p["synthetic"]["items"]), "int")
    shares = [r["share"] for r in p["sweep"] if r["share"] is not None]
    f["sweep.definitions"] = (len(p["sweep"]), "int")
    f["sweep.min"] = (min(shares), "pct")
    f["sweep.max"] = (max(shares), "pct")
    f["sweep.meet_half"] = (sum(v >= 0.5 for v in shares), "int")

    f["robustness.registries"] = (rb["registries"], "int")
    f["robustness.flip_rate"] = (rb["flip_rate"], "pct")
    for prof in ("low", "mid", "high"):
        f[f"robustness.flip_rate.{prof}"] = (rb["by_profile"][prof]["flip_rate"], "pct")
    for ax in ("threshold", "guardrails", "unit", "scope"):
        f[f"robustness.effect.{ax}"] = (rb["effects"][ax], "pct1")
    f["robustness.spread.median"] = (rb["spread"]["0.5"], "pct")

    w = cal["weights"]
    f["calibration.bands.max_changed"] = (cal["bands"]["max_changed"], "int")
    f["calibration.bands.n"] = (cal["bands"]["n"], "int")
    f["calibration.weights.draws"] = (w["draws"], "int")
    f["calibration.weights.spearman_median"] = (w["spearman_median"], "f2")
    f["calibration.weights.spearman_p05"] = (w["spearman_p05"], "f2")
    for k in ("measurement_source", "terms_defined"):
        f[f"calibration.pass_rate.{k}"] = (w["pass_rate"][k], "pct")
        f[f"calibration.leave_one_out.{k}"] = (w["leave_one_out"][k], "f3")
    for k in ("numeric_target", "dated_deadline"):
        c = cal["consistency"][k]
        f[f"calibration.consistency.{k}.agree"] = (c["agree"], "int")
        f[f"calibration.consistency.{k}.n"] = (c["n"], "int")
        f[f"calibration.consistency.{k}.kappa"] = (c["kappa"], "f2")
        f[f"calibration.consistency.{k}.ci_low"] = (c["ci95"][0], "f2")
        f[f"calibration.consistency.{k}.ci_high"] = (c["ci95"][1], "f2")
    f["calibration.consistency.disagreements"] = (cal["consistency"]["disagreements"], "list")

    f["agreement.blind_items"] = (ag["blind_items"], "int")
    for k in ("recall", "numeric_recall"):
        f[f"agreement.{k}.found"] = (ag[k]["found"], "int")
        f[f"agreement.{k}.n"] = (ag[k]["n"], "int")
        f[f"agreement.{k}.rate"] = (ag[k]["rate"], "pct")
        f[f"agreement.{k}.ci_low"] = (ag[k]["ci95"][0], "pct")
        f[f"agreement.{k}.ci_high"] = (ag[k]["ci95"][1], "pct")
    f["agreement.missed"] = (ag["missed"], "list")

    for name, res in _evaluation().items():
        for key, val in res.get("facts", {}).items():
            f[f"{name}.{key}"] = (val["value"], val["format"])
    return f


def compute() -> dict[str, dict]:
    return {k: {"value": v, "text": fmt(v, kind)} for k, (v, kind) in sorted(raw_facts().items())}


def dumps(facts: dict) -> str:
    return json.dumps(facts, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def write() -> Path:
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / "facts.json"
    path.write_text(dumps(compute()), encoding="utf-8", newline="\n")
    return path
