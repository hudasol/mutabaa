"""Time the own file reader and the score on a generated file of N rows (default 200000, the row cap).

    python scripts/benchmark.py [ROWS]

The file is generated in memory from a fixed pattern, so runs are comparable. Timings depend on the machine.
"""

from __future__ import annotations

import sys
import time

from pipeline import own
from pipeline.own_report import assess


def make(n: int) -> str:
    kinds = ("target", "milestone", "deliverable", "input", "projection", "assessment", "vision")
    out = ["id,title,kind,owner,metric,unit,target_number,deadline,measurement_source,undefined_terms"]
    for i in range(n):
        k = kinds[i % 7]
        owner = f"Office {i % 40}" if i % 3 else ""
        source = "Annual report" if i % 2 else ""
        terms = "agentic; service" if i % 4 == 0 else ""
        out.append(
            f'C{i},"Commitment {i}, with a comma",{k},{owner},services,services,{i % 100},'
            f'{2026 + i % 5}-12-31,{source},"{terms}"'
        )
    return "\n".join(out) + "\n"


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    text = make(n)
    t0 = time.perf_counter()
    res = own.load("bench.csv", text)
    t1 = time.perf_counter()
    rows = assess(res)
    t2 = time.perf_counter()
    print(f"rows {n}  accepted {res.accepted}  file {len(text) / 1e6:.1f} MB")
    print(f"read and convert {t1 - t0:.2f} s   score and questions {t2 - t1:.2f} s   total {t2 - t0:.2f} s")
    return 0 if len(rows) == res.accepted else 1


if __name__ == "__main__":
    sys.exit(main())
