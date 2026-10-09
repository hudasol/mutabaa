"""Fail if a test named in docs/TRACEABILITY.md cannot be found in its file."""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
missing = []
for line in (root / "docs" / "TRACEABILITY.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\|[^|]+\|\s*(\S+)\s*::\s*(.+?)\s*\|$", line)
    if not m:
        continue
    f, name = m.groups()
    text = (root / f).read_text(encoding="utf-8") if (root / f).exists() else ""
    if name not in text:
        missing.append(f"{f} :: {name}")
for x in missing:
    print("MISSING", x)
print(f"{len(missing)} missing")
sys.exit(1 if missing else 0)
