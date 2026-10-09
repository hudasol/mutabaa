"""CLI: python -m pipeline validate | rehash | synth | build | verify-live [--write] [--only S01,S02]"""

from __future__ import annotations

import hashlib
import json
import sys

from .io import REAL, ROOT, load_real
from .questions import questions
from .score import score
from .sensitivity import summary, sweep
from .status import status
from .synth import generate
from .validate import file_hash, validate
from .verify_live import dumps as dump_report
from .verify_live import run as run_verify
from .verify_live import summarise


def cmd_validate() -> int:
    errors, warnings = validate()
    for w in warnings:
        print(f"warn  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def cmd_rehash() -> int:
    p = REAL / "sources.json"
    rows = json.loads(p.read_text(encoding="utf-8"))
    for r in rows:
        r["content_hash"] = file_hash(r["extract_file"])
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"rehashed {len(rows)} sources")
    return 0


SYNTH = ROOT / "data" / "synthetic"
GOLDEN = ROOT / "data" / "golden"


def cmd_synth() -> int:
    """Regenerate the synthetic registry and the golden sensitivity file."""
    reg = generate()
    SYNTH.mkdir(parents=True, exist_ok=True)
    GOLDEN.mkdir(parents=True, exist_ok=True)
    (SYNTH / "registry.json").write_text(
        json.dumps(reg.model_dump(mode="json"), indent=1) + "\n", encoding="utf-8"
    )
    rows = sweep(reg)
    (GOLDEN / "sensitivity.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    print(f"registry: {len(reg.entities)} entities, {len(reg.items)} items; {summary(rows)}")
    return 0


def cmd_verify_live(args: list[str]) -> int:
    """Fetch each source page and check the figures the notes rely on. Needs network access."""
    only = None
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    d = load_real()
    rep = run_verify(d.sources, only=only)
    print(summarise(rep))
    if "--write" in args:
        path = REAL / "verification.json"
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"results": {}}
        old["results"].update(rep["results"])
        old.update({k: v for k, v in rep.items() if k != "results"})
        path.write_text(dump_report(old), encoding="utf-8")
        print(f"wrote {path}")
    failed = [k for k, v in rep["results"].items() if v["result"] == "failed"]
    return 1 if failed else 0


def data_as_of(d):
    return max(s.retrieved for s in d.sources)


def derive():
    d = load_real()
    src = {s.id: s for s in d.sources}
    asof = data_as_of(d)
    scores = [score(c) for c in d.commitments]
    statuses = [status(c, d.evidence, src, asof) for c in d.commitments]
    return d, scores, statuses


def coverage(d) -> list[dict]:
    """For each commitment: how many searches touched it, when last, and what they found."""
    rows = []
    for c in d.commitments:
        qs = [q for q in d.searches if c.id in q.commitment_ids]
        rows.append(
            {
                "commitment_id": c.id,
                "searches": len(qs),
                "last_searched": max((q.searched_on.isoformat() for q in qs), default=None),
                "found_sources": sorted({sid for q in qs for sid in q.found_source_ids}),
                "outcomes": sorted({q.outcome for q in qs}),
            }
        )
    return rows


def cmd_build() -> int:
    if cmd_validate():
        return 1
    d, scores, statuses = derive()
    out = ROOT / "site" / "src" / "data"
    out.mkdir(parents=True, exist_ok=True)
    qs = {c.id: questions(c, sc) for c, sc in zip(d.commitments, scores, strict=True)}
    payload = {
        "sources": [s.model_dump(mode="json") for s in d.sources],
        "commitments": [c.model_dump(mode="json") for c in d.commitments],
        "evidence": [e.model_dump(mode="json") for e in d.evidence],
        "claims": [k.model_dump(mode="json") for k in d.claims],
        "scores": [s.model_dump(mode="json") for s in scores],
        "statuses": [s.model_dump(mode="json") for s in statuses],
        "questions": qs,
        "coverage": coverage(d),
        "searches": [q.model_dump(mode="json") for q in d.searches],
        "verification": d.verification,
        "synthetic": json.loads((SYNTH / "registry.json").read_text(encoding="utf-8")),
        "sweep": json.loads((GOLDEN / "sensitivity.json").read_text(encoding="utf-8")),
    }
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1)
    payload["build"] = {
        "data_as_of": data_as_of(d).isoformat(),
        "payload_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "schema": 2,
    }
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1) + "\n"
    (out / "real.json").write_text(text, encoding="utf-8")
    print(f"wrote {out / 'real.json'}")
    return 0


def main(argv: list[str]) -> int:
    cmds = {"validate": cmd_validate, "rehash": cmd_rehash, "synth": cmd_synth, "build": cmd_build}
    if len(argv) >= 2 and argv[1] == "verify-live":
        return cmd_verify_live(argv[2:])
    if len(argv) != 2 or argv[1] not in cmds:
        print(__doc__)
        return 2
    return cmds[argv[1]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
