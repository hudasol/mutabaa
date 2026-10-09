"""Compare two payloads (for example the committed one and a rebuild) and list what changed."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .io import ROOT

PAYLOAD = "site/src/data/real.json"


def load_at(ref: str) -> dict:
    out = subprocess.run(
        ["git", "show", f"{ref}:{PAYLOAD}"], capture_output=True, text=True, check=True, cwd=ROOT
    )
    return json.loads(out.stdout)


def load_current() -> dict:
    return json.loads(Path(ROOT / PAYLOAD).read_text(encoding="utf-8"))


def diff(old: dict, new: dict) -> list[str]:
    lines: list[str] = []
    oc = {c["id"]: c for c in old["commitments"]}
    nc = {c["id"]: c for c in new["commitments"]}
    for i in sorted(nc.keys() - oc.keys()):
        lines.append(f"+ {i} added: {nc[i]['title']}")
    for i in sorted(oc.keys() - nc.keys()):
        lines.append(f"- {i} removed: {oc[i]['title']}")
    for i in sorted(oc.keys() & nc.keys()):
        for k in ("title", "target", "unit", "deadline", "owner", "metric", "kind"):
            if oc[i].get(k) != nc[i].get(k):
                lines.append(f"~ {i} {k}: {oc[i].get(k)!r} -> {nc[i].get(k)!r}")
    os_ = {s["commitment_id"]: s for s in old["statuses"]}
    ns = {s["commitment_id"]: s for s in new["statuses"]}
    for i in sorted(os_.keys() & ns.keys()):
        if os_[i]["status"] != ns[i]["status"]:
            lines.append(f"~ {i} status: {os_[i]['status']} -> {ns[i]['status']}")
        if not os_[i].get("stale") and ns[i].get("stale"):
            lines.append(f"! {i} evidence became stale")
    osc = {s["commitment_id"]: s for s in old["scores"]}
    nsc = {s["commitment_id"]: s for s in new["scores"]}
    for i in sorted(osc.keys() & nsc.keys()):
        if osc[i]["band"] != nsc[i]["band"]:
            lines.append(f"~ {i} band: {osc[i]['band']} -> {nsc[i]['band']}")
    ov = {k: v["result"] for k, v in old["verification"]["results"].items()}
    nv = {k: v["result"] for k, v in new["verification"]["results"].items()}
    for k in sorted(ov.keys() & nv.keys()):
        if ov[k] != nv[k]:
            lines.append(f"~ source {k} verification: {ov[k]} -> {nv[k]}")
    return lines
