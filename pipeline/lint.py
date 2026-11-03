"""Commitment linter: read one sentence and say which of the six checks it passes.

Deterministic and offline. No model judgement. The rules are word lists and patterns in
data/config/lint_rules.json. The TypeScript port in site/src/lint.ts reads the same file, and the golden
files data/golden/lint_inputs.json and data/golden/lint_outputs.json keep both identical.

The linter never invents a number, an owner or a date. It reports what the wording contains, what it lacks,
and the question to answer for each gap. A user may supply a missing field; the score is then recomputed
and shown beside the score of the wording alone.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import cache, lru_cache
from typing import Any

from .io import ROOT
from .own import deadline_precision
from .questions import questions
from .score import score

_A = re.ASCII
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
MAX_TEXT = 4000
SLOTS = {
    "numeric_target": "target_number",
    "unit_defined": "unit",
    "dated_deadline": "deadline",
    "owner_named": "owner",
    "measurement_source": "measurement_source",
    "terms_defined": "defined_terms",
}


@lru_cache(maxsize=1)
def rules() -> dict[str, Any]:
    return json.loads((ROOT / "data" / "config" / "lint_rules.json").read_text(encoding="utf-8"))


def normalise(text: str) -> str:
    t = text[:MAX_TEXT].translate(_DIGITS).replace("٪", "%").replace("٫", ".").replace("٬", ",")
    return " ".join(t.split())


def short_title(t: str) -> str:
    if len(t) <= 80:
        return t
    cut = t[:80]
    i = cut.rfind(" ")
    return (cut if i < 0 else cut[:i]) + "…"


def _ci(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.IGNORECASE | _A)


@cache
def _alt(key: str) -> re.Pattern[str]:
    return _ci("|".join(f"(?:{p})" for p in rules()[key]))


@dataclass
class Parsed:
    target_number: float | None = None
    unit: str | None = None
    deadline_text: str | None = None
    deadline_precision: str = "none"
    owner: str | None = None
    measurement_source: str | None = None
    undefined_terms: list[str] = field(default_factory=list)


_START_WORDS = re.compile(
    r"(?:since|from|after|announced|dated|following|as of|of the)\s*$", _A | re.IGNORECASE
)


def _date_phrases(n: str) -> list[tuple[int, int, str]]:
    m = rules()["month_names"]
    pats = [
        r"\d{4}-\d{2}-\d{2}",
        rf"\d{{1,2}} (?:{m})\.?,? \d{{4}}",
        rf"(?:{m})\.? \d{{1,2}},? \d{{4}}",
        rf"(?:{m})\.?,? \d{{4}}",
        r"q[1-4] \d{4}",
        r"(?<![\d.,])(?:19|20)\d{2}(?![\d%])",
    ]
    taken: list[tuple[int, int, str]] = []
    for p in pats:
        for mt in _ci(p).finditer(n):
            s, e = mt.span()
            if any(s < b and a < e for a, b, _ in taken):
                continue
            taken.append((s, e, mt.group(0)))
    return sorted(taken)


def _year_of(phrase: str) -> int:
    ys = re.findall(r"(?:19|20)\d{2}", phrase, _A)
    return int(ys[-1]) if ys else 0


_PREC_RANK = {"day": 3, "month": 2, "year": 1}


def _number(rest: str, r: dict[str, Any]) -> tuple[float | None, int, int, str]:
    """First number in the text with dates removed: (value, start, end, kind of match)."""
    best: tuple[int, float, int, str] | None = None
    pw = "|".join(re.escape(w) for w in r["percent_words"])
    for mt in _ci(rf"(\d+(?:\.\d+)?)\s*(?:{pw})").finditer(rest):
        best = (mt.start(), float(mt.group(1)), mt.end(), "percent")
        break
    hw = "|".join(re.escape(w) for w in r["half_words"])
    for mt in _ci(rf"(?<![a-z])(?:{hw})(?![a-z])").finditer(rest):
        if best is None or mt.start() < best[0]:
            best = (mt.start(), 50.0, mt.end(), "percent")
        break
    mags = r["magnitudes"]
    mg = "|".join(re.escape(k) for k in sorted(mags, key=len, reverse=True))
    for mt in _ci(rf"(?<![\d.,a-z])(\d[\d,]*(?:\.\d+)?)(?:\s*({mg})(?![a-z]))?").finditer(rest):
        raw = mt.group(1).rstrip(",").replace(",", "")
        try:
            v = float(raw)
        except ValueError:
            continue
        if mt.group(2):
            v *= mags[mt.group(2).lower()]
        if best is None or mt.start() < best[0]:
            best = (mt.start(), v, mt.end(), "amount")
        break
    if best is None:
        return None, 0, 0, ""
    return best[1], best[0], best[2], best[3]


def _unit(rest: str, number_start: int, number_end: int, r: dict[str, Any]) -> str | None:
    cur = _ci(r"(aed|usd|\$|dh|درهم)\s*$").search(rest[:number_start])
    if cur:
        return "usd" if cur.group(1).lower() in ("usd", "$") else "aed"
    after = rest[number_end:number_end + 80]
    best: tuple[int, int, str] | None = None
    for order, (unit, words) in enumerate(r["units"].items()):
        pat = _ci("(?<![a-z0-9])(?:" + "|".join(words) + ")(?![a-z0-9])")
        mt = pat.search(after)
        if mt and (best is None or (mt.start(), order) < (best[0], best[1])):
            best = (mt.start(), order, unit)
    return best[2] if best else None


def parse(text: str) -> Parsed:
    r = rules()
    n = normalise(text)
    out = Parsed()
    dates = [d for d in _date_phrases(n) if not _START_WORDS.search(n[max(0, d[0] - 14):d[0]])]
    all_dates = _date_phrases(n)
    # deadline
    pick: tuple[int, int, str] | None = None
    for _s, _e, ph in dates:
        prec = deadline_precision(ph)
        if prec not in _PREC_RANK:
            continue
        key = (_year_of(ph), _PREC_RANK[prec])
        if pick is None or key > (pick[0], pick[1]):
            pick = (key[0], key[1], ph)
    if pick:
        out.deadline_text, out.deadline_precision = pick[2], deadline_precision(pick[2])
    else:
        rel = _alt("relative_cues").search(n.lower())
        if rel:
            out.deadline_text, out.deadline_precision = rel.group(0).strip(" .,;:"), "relative"
    # number and unit, with every date phrase removed first so that years and days are not read as targets
    chars = list(n)
    for s, e, _ph in all_dates:
        for i in range(s, e):
            chars[i] = " "
    rest = "".join(chars)
    value, start, end, _kind = _number(rest, r)
    out.target_number = value
    if value is not None:
        out.unit = _unit(rest, start, end, r)
    # owner
    best: tuple[int, int, str] | None = None
    for order, p in enumerate(r["owner_patterns"]):
        mt = re.search(p, n, _A)
        if mt and (best is None or (mt.start(), order) < (best[0], best[1])):
            best = (mt.start(), order, mt.group(0).strip())
    out.owner = best[2] if best else None
    low = n.lower()
    mt2 = _alt("measure_cues").search(low)
    out.measurement_source = mt2.group(0).strip() if mt2 else None
    if not _alt("definition_cues").search(low):
        for v in r["vague_terms"]:
            pat = _ci("(?<![a-z])(?:" + "|".join(v["patterns"]) + ")(?![a-z])")
            if pat.search(low):
                out.undefined_terms.append(v["term"])
    return out


@dataclass
class _Row:
    id: str
    title: str
    title_ar: str
    kind: str
    owner: str | None
    unit: str | None
    target_number: float | None
    deadline_precision: str
    measurement_source: str | None
    undefined_terms: list[str]


def _result(row: _Row) -> dict[str, Any]:
    s = score(row)
    return {"checks": s.checks, "applicable": s.applicable, "passed": s.passed, "ratio": s.ratio,
            "band": s.band, "missing": s.missing}


def _row(title: str, kind: str, p: Parsed) -> _Row:
    return _Row("LINT", title, title, kind, p.owner, p.unit, p.target_number, p.deadline_precision,
                p.measurement_source, p.undefined_terms)


def lint(text: str, kind: str = "target", fields: dict[str, Any] | None = None) -> dict[str, Any]:
    """Score the wording alone ("before") and, when fields are supplied, with them ("after")."""
    n = normalise(text)
    p = parse(text)
    title = short_title(n)
    before_row = _row(title, kind, p)
    before = _result(before_row)
    qs = [{**q, "slot": SLOTS[q["check"]]} for q in questions(before_row, score(before_row))]
    out: dict[str, Any] = {
        "kind": kind,
        "text": n,
        "found": {
            "target_number": p.target_number, "unit": p.unit, "deadline_text": p.deadline_text,
            "deadline_precision": p.deadline_precision, "owner": p.owner,
            "measurement_source": p.measurement_source, "undefined_terms": p.undefined_terms,
        },
        "before": before,
        "questions": qs,
        "after": None,
        "after_found": None,
    }
    f = {k: v for k, v in (fields or {}).items() if v not in (None, "", [])}
    if f:
        a = Parsed(p.target_number, p.unit, p.deadline_text, p.deadline_precision, p.owner,
                   p.measurement_source, list(p.undefined_terms))
        if "target_number" in f:
            a.target_number = float(f["target_number"])
        if "unit" in f:
            a.unit = str(f["unit"]).strip() or a.unit
        if "deadline" in f:
            a.deadline_text = str(f["deadline"]).strip()
            a.deadline_precision = deadline_precision(a.deadline_text)
        if "owner" in f:
            a.owner = str(f["owner"]).strip() or a.owner
        if "measurement_source" in f:
            a.measurement_source = str(f["measurement_source"]).strip() or a.measurement_source
        if "defined_terms" in f:
            done = {str(t).strip().lower() for t in f["defined_terms"]}
            a.undefined_terms = [t for t in a.undefined_terms if t.lower() not in done]
        out["after"] = _result(_row(title, kind, a))
        out["after_found"] = {
            "target_number": a.target_number, "unit": a.unit, "deadline_text": a.deadline_text,
            "deadline_precision": a.deadline_precision, "owner": a.owner,
            "measurement_source": a.measurement_source, "undefined_terms": a.undefined_terms,
        }
    return out
