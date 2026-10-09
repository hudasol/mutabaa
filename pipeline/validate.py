"""Integrity checks for the real dataset.

Errors fail the build. Every check exists because a specific mistake is easy to make by hand:
a misquoted anchor, a stale hash, media evidence labelled as official, a unit that drifted.
"""

from __future__ import annotations

import hashlib
import re
from datetime import date

from .io import ROOT, RealData, load_real
from .schemas import Source

_WS = re.compile(r"\s+")


def norm(text: str) -> str:
    return _WS.sub(" ", text).strip().lower()


def file_hash(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def validate(data: RealData | None = None) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    d = data or load_real()
    errors: list[str] = []
    warnings: list[str] = []
    src: dict[str, Source] = {}
    texts: dict[str, str] = {}

    for coll, name in (
        (d.sources, "source"),
        (d.commitments, "commitment"),
        (d.evidence, "evidence"),
        (d.claims, "claim"),
    ):
        ids = [x.id for x in coll]
        for i in {i for i in ids if ids.count(i) > 1}:
            errors.append(f"duplicate {name} id {i}")

    for s in d.sources:
        src[s.id] = s
        p = ROOT / s.extract_file
        if not p.exists():
            errors.append(f"{s.id}: extract file {s.extract_file} missing")
            continue
        texts[s.id] = norm(p.read_text(encoding="utf-8"))
        if file_hash(s.extract_file) != s.content_hash:
            errors.append(f"{s.id}: content_hash is stale (run `python -m pipeline rehash`)")
        if s.published and s.published > s.retrieved:
            errors.append(f"{s.id}: published after retrieved")

    def anchor_ok(sid: str, text: str, where: str) -> None:
        if sid not in src:
            errors.append(f"{where}: unknown source {sid}")
        elif norm(text) not in texts.get(sid, ""):
            errors.append(f"{where}: anchor not found in {sid} extract: {text!r}")

    cids = {c.id for c in d.commitments}
    for c in d.commitments:
        for sid in c.source_ids:
            if sid not in src:
                errors.append(f"{c.id}: unknown source {sid}")
        for a in c.anchors:
            if a.source_id not in c.source_ids:
                errors.append(f"{c.id}: anchor source {a.source_id} not in source_ids")
            anchor_ok(a.source_id, a.text, c.id)
        if all(src[s].kind == "secondary-media" for s in c.source_ids if s in src):
            warnings.append(f"{c.id}: sourced only from secondary media")
        if all(src[s].ai_assisted for s in c.source_ids if s in src):
            errors.append(f"{c.id}: sourced only from AI-assisted material")
        if c.announced and c.deadline and c.deadline < c.announced:
            errors.append(f"{c.id}: deadline precedes announcement")

    for e in d.evidence:
        for cid in e.commitment_ids:
            if cid not in cids:
                errors.append(f"{e.id}: unknown commitment {cid}")
        anchor_ok(e.source_id, e.anchor, e.id)
        s = src.get(e.source_id)
        if s:
            if s.kind == "secondary-media" and e.corroboration == "official-confirmed":
                errors.append(f"{e.id}: media source cannot be 'official-confirmed'")
            if s.kind != "secondary-media" and e.corroboration != "official-confirmed":
                errors.append(f"{e.id}: official source marked {e.corroboration}")
            if e.as_of and e.as_of > s.retrieved:
                errors.append(f"{e.id}: as_of after retrieval")
        if e.kind == "quantified-progress" and (e.value is None or e.unit is None):
            errors.append(f"{e.id}: quantified-progress needs value and unit")
        if e.kind != "quantified-progress" and e.as_of is None and not e.as_of_note:
            warnings.append(f"{e.id}: no as_of date")

    for k in d.claims:
        anchor_ok(k.source_id, k.anchor, k.id)
        for cid in k.commitment_ids:
            if cid not in cids:
                errors.append(f"{k.id}: unknown commitment {cid}")
        for sid in k.official_sources_checked:
            if sid in src and src[sid].kind == "secondary-media":
                errors.append(f"{k.id}: checked source {sid} is not official")

    # every real commitment has an owner-less warning, so gaps stay visible
    for c in d.commitments:
        if c.owner is None and c.kind not in ("projection",):
            warnings.append(f"{c.id}: no owner named")
    _ = date  # keep import explicit for type checkers
    return errors, warnings
