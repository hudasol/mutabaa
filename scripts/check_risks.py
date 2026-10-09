"""Fail if a row of docs/RISKS.md has an empty field."""
import sys
from pathlib import Path

text = (Path(__file__).resolve().parent.parent / "docs" / "RISKS.md").read_text(encoding="utf-8")
rows = [r for r in text.splitlines() if r.startswith("| R")]
bad = [r for r in rows if any(not c.strip() for c in r.strip("|").split("|"))]
print(f"{len(rows)} risks, {len(bad)} incomplete")
sys.exit(1 if bad or not rows else 0)
