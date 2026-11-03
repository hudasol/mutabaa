"""Merge extraction staging files into data/real (sources, commitments and extraction notes).

Usage: python scripts/ingest_staging.py stage1.json [stage2.json ...]

Reads files written to the brief in the staging format, assigns the next free S and C identifiers in
file order, writes each extraction note under data/real/extracts, hashes it the way `validate` does,
and validates every commitment with the pydantic model before anything is written. Nothing is written
if any record fails. The command line is deterministic: the same files give the same result.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.schemas import UNITS, Commitment, Source  # noqa: E402

REAL = ROOT / "data" / "real"


def _norm(text: str) -> str:
    return " ".join(text.split()).lower()


def main(paths: list[str]) -> int:
    sources = json.loads((REAL / "sources.json").read_text(encoding="utf-8"))
    commitments = json.loads((REAL / "commitments.json").read_text(encoding="utf-8"))
    have_urls = {s["url"].rstrip("/") for s in sources}
    next_s = max(int(s["id"][1:]) for s in sources) + 1
    next_c = max(int(c["id"][1:]) for c in commitments) + 1
    new_sources, new_commitments, notes, problems = [], [], {}, []

    for path in paths:
        stage = json.loads(Path(path).read_text(encoding="utf-8"))
        keymap: dict[str, str] = {}
        for s in stage["sources"]:
            if s["url"].rstrip("/") in have_urls:
                problems.append(f"{path}: duplicate url skipped {s['url']}")
                continue
            sid = f"S{next_s:02d}"
            next_s += 1
            keymap[s["key"]] = sid
            have_urls.add(s["url"].rstrip("/"))
            rel = f"data/real/extracts/{sid}.md"
            text = s["note"].replace(f"# {s['key']}:", f"# {sid}:", 1).replace("\r\n", "\n").rstrip() + "\n"
            notes[rel] = text
            row = {
                "id": sid, "title": s["title"], "publisher": s["publisher"],
                "url": s["url"], "kind": s["kind"],
                "published": s.get("published"), "published_note": s.get("published_note"),
                "retrieved": s["retrieved"], "extract_file": rel,
                "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "ai_assisted": True, "notes": s.get("notes", ""),
                "expect_present": s.get("expect_present", []), "expect_absent": s.get("expect_absent", []),
            }
            try:
                Source.model_validate(row)
            except ValidationError as e:
                problems.append(f"{sid}: {e.errors()[0]['msg']}")
            new_sources.append(row)
        for c in stage["commitments"]:
            ids = [keymap[k] for k in c["source_keys"] if k in keymap]
            if not ids:
                problems.append(f"{path}: commitment without a kept source: {c['title']}")
                continue
            cid = f"C{next_c:02d}"
            next_c += 1
            unit = c.get("unit")
            if unit not in UNITS:
                unit = None
            tags = list(c.get("tags", []))
            if c.get("emirate_tag") and c["emirate_tag"] not in tags:
                tags.append(c["emirate_tag"])
            has_number = c.get("target_number") is not None
            ms = c.get("measurement_source")
            if ms and ms.strip().lower() in ("not stated", "none", "n/a"):
                ms = None
            row = {
                "id": cid, "title": c["title"], "title_ar": c["title_ar"], "statement": c["statement"],
                "statement_ar": c["statement_ar"], "jurisdiction": c["jurisdiction"], "kind": c["kind"],
                "owner": c.get("owner"), "metric": c.get("metric"), "unit": unit,
                "baseline": c.get("baseline"),
                "target_value": c.get("target_value"), "target_number": c.get("target_number"),
                "target_comparator": c.get("target_comparator") if has_number else None,
                "deadline": c.get("deadline"), "deadline_text": c.get("deadline_text"),
                "deadline_precision": c.get("deadline_precision", "none"),
                "measurement_source": ms, "undefined_terms": c.get("undefined_terms", []),
                "announced": c.get("announced"), "tags": tags, "source_ids": ids,
                "anchors": [
                    {"source_id": keymap[a["source_key"]], "text": a["text"]}
                    for a in c["anchors"] if a["source_key"] in keymap
                ],
                "notes": c.get("notes", ""),
            }
            try:
                m = Commitment.model_validate(row)
            except ValidationError as e:
                problems.append(f"{cid} {c['title']}: {e.errors()[0]['msg']}")
                continue
            for a in m.anchors:
                rel = f"data/real/extracts/{a.source_id}.md"
                if _norm(a.text) not in _norm(notes.get(rel, "")):
                    problems.append(f"{cid}: anchor not in note {a.source_id}: {a.text!r}")
            new_commitments.append(m.model_dump(mode="json", exclude_defaults=True))

    for p in problems:
        print("problem:", p)
    if [p for p in problems if "duplicate url" not in p]:
        print("not written: fix the problems above")
        return 1
    for rel, text in notes.items():
        (ROOT / rel).write_text(text, encoding="utf-8", newline="\n")
    (REAL / "sources.json").write_text(
        json.dumps(sources + new_sources, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (REAL / "commitments.json").write_text(
        json.dumps(commitments + new_commitments, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"added {len(new_sources)} sources and {len(new_commitments)} commitments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
