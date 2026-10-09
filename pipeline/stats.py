"""Small, dependency-free statistics helpers (seeded, deterministic)."""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence


def ranks(xs: Sequence[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a: Sequence[float], b: Sequence[float]) -> float | None:
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va == 0 or vb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b, strict=True)) / math.sqrt(va * vb)


def spearman(a: Sequence[float], b: Sequence[float]) -> float | None:
    return pearson(ranks(a), ranks(b))


def quantile(xs: Sequence[float], q: float) -> float:
    s = sorted(xs)
    pos = q * (len(s) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def cohen_kappa(a: Sequence[bool], b: Sequence[bool]) -> float | None:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b, strict=True)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    if pe == 1:
        return None
    return (po - pe) / (1 - pe)


def bootstrap_ci(
    n: int, stat: Callable[[list[int]], float | None], reps: int = 2000, seed: int = 7, alpha: float = 0.05
) -> tuple[float, float]:
    """Percentile bootstrap over row indices. `stat` receives a resampled index list."""
    rng = random.Random(seed)
    vals = []
    for _ in range(reps):
        v = stat([rng.randrange(n) for _ in range(n)])
        if v is not None:
            vals.append(v)
    return round(quantile(vals, alpha / 2), 4), round(quantile(vals, 1 - alpha / 2), 4)
