"""Weekly drift check: compare a fresh run of the live verifier with the recorded one.

The recorded run is data/real/verification.json. A page counts as changed when its result differs or when
its visible text hash differs from the recorded hash. This module never edits a ledger record; it only
produces a dated report. The network run itself is in verify_live.py.
"""

from __future__ import annotations

from typing import Any

CHANGED = ("verified", "failed", "no-expectations")


def compare(baseline: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    old = baseline.get("results", {})
    out: dict[str, list[dict[str, Any]]] = {
        "changed": [], "newly_unreachable": [], "still_unreachable": [], "recovered": [], "unchanged": [],
    }
    for sid in sorted(report["results"]):
        new = report["results"][sid]
        prev = old.get(sid)
        row = {"id": sid, "was": prev["result"] if prev else None, "now": new["result"]}
        if new["result"] == "unreachable":
            same = prev is not None and prev["result"] == "unreachable"
            key = "still_unreachable" if same else "newly_unreachable"
            out[key].append(row | {"error": new.get("error")})
            continue
        if prev is None or prev["result"] == "unreachable":
            out["recovered"].append(row)
            continue
        h_old, h_new = prev.get("visible_text_sha256"), new.get("visible_text_sha256")
        if prev["result"] != new["result"]:
            out["changed"].append(row | {"reason": "result"})
        elif h_old and h_new and h_old != h_new:
            out["changed"].append(row | {"reason": "visible text hash"})
        else:
            out["unchanged"].append(row)
    return {"run_at": report.get("run_at"), "counts": {k: len(v) for k, v in out.items()}, **out}


def needs_attention(cmp: dict[str, Any]) -> bool:
    """An issue is warranted for a changed page or a page that has just become unreachable."""
    return bool(cmp["changed"] or cmp["newly_unreachable"])


def render(date: str, cmp: dict[str, Any]) -> str:
    c = cmp["counts"]
    lines = [
        f"# Source drift report, {date}",
        "",
        "Pages are compared with the last recorded verification (`data/real/verification.json`). "
        "No ledger record was changed by this run. A changed page needs a person to read it; "
        "an unreachable page is recorded and is not used as evidence.",
        "",
        f"Changed: {c['changed']}. Newly unreachable: {c['newly_unreachable']}. "
        f"Still unreachable: {c['still_unreachable']}. Recovered: {c['recovered']}. "
        f"Unchanged: {c['unchanged']}.",
        "",
    ]
    for key, title in (("changed", "Changed"), ("newly_unreachable", "Newly unreachable"),
                       ("recovered", "Recovered"), ("still_unreachable", "Still unreachable")):
        if cmp[key]:
            lines.append(f"## {title}")
            for r in cmp[key]:
                extra = r.get("reason") or r.get("error") or ""
                lines.append(f"- {r['id']}: {r['was']} to {r['now']}" + (f" ({extra})" if extra else ""))
            lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"
