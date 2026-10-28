"""Score the commitments in an office's own file and format the result for a terminal, a script or a sheet."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter
from typing import Any

from .own import OwnResult
from .questions import questions
from .score import LABELS, score


def _safe(v: str) -> str:
    """Neutralise spreadsheet formula injection: a leading = + - @ tab or CR gets an apostrophe."""
    return "'" + v if v[:1] in ("=", "+", "-", "@", "\t", "\r") else v


# The wording the site shows. The identifiers stay in JSON because code depends on them (docs/adr/0007).
WORDING = {
    "checkable": "fully specified",
    "partly-checkable": "partly specified",
    "not-yet-checkable": "under-specified",
}
BANDS = ("checkable", "partly-checkable", "not-yet-checkable")


def assess(res: OwnResult) -> list[dict[str, Any]]:
    """One record per accepted commitment: score, what it lacks and the questions that close the gap."""
    out = []
    for c in res.items:
        s = score(c)
        out.append(
            {
                "id": c.id, "title": c.title, "kind": c.kind, "row": c.row, "passed": s.passed,
                "applicable": s.applicable, "ratio": s.ratio, "band": s.band, "checks": s.checks,
                "missing": s.missing, "questions": questions(c, s),
            }
        )
    return out


def summary(res: OwnResult, rows: list[dict[str, Any]]) -> dict[str, Any]:
    bands = Counter(r["band"] for r in rows)
    ratios = [r["ratio"] for r in rows]
    gaps = Counter(m for r in rows for m in r["missing"])
    return {
        "rows": res.rows, "accepted": res.accepted, "rejected": res.rejected, "duplicates": res.duplicates,
        "truncated": res.truncated, "unmapped_columns": res.unmapped,
        "mean_ratio": round(sum(ratios) / len(ratios), 4) if ratios else None,
        "min_ratio": min(ratios) if ratios else None,
        "bands": {b: bands.get(b, 0) for b in BANDS},
        "most_common_gaps": [{"check": k, "count": v} for k, v in gaps.most_common()],
    }


def as_json(res: OwnResult, rows: list[dict[str, Any]], with_questions: bool) -> str:
    items = rows if with_questions else [{k: v for k, v in r.items() if k != "questions"} for r in rows]
    return json.dumps({"summary": summary(res, rows), "errors": res.errors, "commitments": items},
                      ensure_ascii=False, indent=2) + "\n"


def as_csv(rows: list[dict[str, Any]]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n", quoting=csv.QUOTE_ALL)
    w.writerow(["id", "title", "kind", "passed", "applicable", "ratio", "band", "missing"])
    for r in rows:
        w.writerow([_safe(r["id"]), _safe(r["title"]), r["kind"], r["passed"], r["applicable"], r["ratio"],
                    r["band"], "; ".join(r["missing"])])
    return buf.getvalue()


def as_text(res: OwnResult, rows: list[dict[str, Any]], lang: str, with_questions: bool) -> str:
    s = summary(res, rows)
    rejected = f", {res.rejected} rejected" if res.rejected else ""
    lines = [f"{res.accepted} of {res.rows} rows read{rejected}"]
    if res.truncated:
        lines.append("The file was cut at the row limit.")
    if rows:
        b = s["bands"]
        lines.append(
            f"fully specified {b['checkable']}, partly specified {b['partly-checkable']}, "
            f"under-specified {b['not-yet-checkable']}; mean score {s['mean_ratio']:.2f}"
        )
        lines.append("")
        wid = max(len(r["id"]) for r in rows)
        for r in rows:
            miss = ", ".join(LABELS[m].lower() for m in r["missing"]) or "nothing missing"
            band = WORDING[r["band"]]
            lines.append(f"{r['id']:<{wid}}  {r['passed']}/{r['applicable']}  {band:<16}  {miss}")
            if with_questions:
                for q in r["questions"]:
                    for lg in (("en", "ar") if lang == "both" else (lang,)):
                        lines.append(f"{'':<{wid}}    - {q[lg]}")
        if s["most_common_gaps"]:
            gaps = "; ".join(f"{LABELS[g['check']].lower()} ({g['count']})" for g in s["most_common_gaps"])
            lines += ["", f"Most common gaps: {gaps}"]
    if res.errors:
        lines += ["", f"{len(res.errors)} problem(s) in the file:"] + [f"  {e}" for e in res.errors[:20]]
        if len(res.errors) > 20:
            lines.append(f"  and {len(res.errors) - 20} more")
    return "\n".join(lines) + "\n"

