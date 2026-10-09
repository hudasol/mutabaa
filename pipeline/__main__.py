"""CLI: python -m pipeline validate | rehash | build"""

from __future__ import annotations

import json
import sys

from .io import REAL, ROOT, load_real
from .score import score
from .status import status
from .validate import file_hash, validate


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


def derive():
    d = load_real()
    src = {s.id: s for s in d.sources}
    scores = [score(c) for c in d.commitments]
    statuses = [status(c, d.evidence, src) for c in d.commitments]
    return d, scores, statuses


def cmd_build() -> int:
    if cmd_validate():
        return 1
    d, scores, statuses = derive()
    out = ROOT / "site" / "src" / "data"
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "sources": [s.model_dump(mode="json") for s in d.sources],
        "commitments": [c.model_dump(mode="json") for c in d.commitments],
        "evidence": [e.model_dump(mode="json") for e in d.evidence],
        "claims": [k.model_dump(mode="json") for k in d.claims],
        "scores": [s.model_dump(mode="json") for s in scores],
        "statuses": [s.model_dump(mode="json") for s in statuses],
    }
    (out / "real.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"wrote {out / 'real.json'}")
    return 0


def main(argv: list[str]) -> int:
    cmds = {"validate": cmd_validate, "rehash": cmd_rehash, "build": cmd_build}
    if len(argv) != 2 or argv[1] not in cmds:
        print(__doc__)
        return 2
    return cmds[argv[1]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
