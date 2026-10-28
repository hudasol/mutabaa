"""Synthetic generator B, written from its specification in PREREGISTRATION.md (experiment E2) only.

It differs from generator A on purpose: entity level effects, guardrail flags that share one latent and
are correlated with maturity, heavy tailed entity sizes and volumes. Nothing here is real.
"""

from __future__ import annotations

import random
from typing import cast

from .schemas import Audience, MaturityLevel, Registry, RegistryMeta, ServiceItem, SyntheticEntity
from .synth import _OPERATION_NAMES, _SERVICE_NAMES, DISCLAIMER, SECTORS

GENERATOR_VERSION = "B-1.0"
PROFILE_MEANS = {"low": 1.0, "mid": 2.0, "high": 3.0}
FLAG_CUTS = (("oversight", -0.3), ("audit_trail", -0.1), ("uae_residency", -0.8), ("fallback", 0.1))


def generate_b(seed: int, n_entities: int = 16, profile: str = "mid") -> Registry:
    rng = random.Random(seed)
    m = PROFILE_MEANS[profile]
    entities: list[SyntheticEntity] = []
    items: list[ServiceItem] = []
    for i in range(n_entities):
        sector = SECTORS[i % len(SECTORS)]
        u = rng.gauss(m, 0.7)
        k = min(120, 10 + int(12 * rng.paretovariate(1.5)))
        o = rng.betavariate(2, 5)
        e = SyntheticEntity(
            id=f"SE{i + 1:02d}",
            name=f"Synthetic {sector} Office {chr(65 + i // len(SECTORS))}",
            sector=sector,
            advancement=round(min(1.0, max(0.0, u / 4)), 3),
        )
        entities.append(e)
        for j in range(k):
            operation = rng.random() < o
            audience: Audience = (
                "internal" if operation else ("citizen" if rng.random() < 0.6 else "business")
            )
            z = u + rng.gauss(0, 0.6) - (0.5 if operation else 0.0)
            maturity = cast(MaturityLevel, max(0, min(4, round(z))))
            g = 0.5 * (z - 2) + rng.gauss(0, 1)
            flags = {name: g + rng.gauss(0, 0.8) > cut for name, cut in FLAG_CUTS}
            if operation:
                tx = 0 if rng.random() < 0.6 else int(50 * rng.paretovariate(1.1))
            else:
                tx = int(200 * rng.paretovariate(1.1))
            items.append(
                ServiceItem(
                    id=f"{e.id}-{j + 1:03d}",
                    entity_id=e.id,
                    sector=sector,
                    kind="operation" if operation else "service",
                    audience=audience,
                    name=(_OPERATION_NAMES if operation else _SERVICE_NAMES)[j % 8],
                    annual_transactions=tx,
                    maturity=maturity,
                    oversight=flags["oversight"],
                    audit_trail=flags["audit_trail"],
                    uae_residency=flags["uae_residency"],
                    fallback=flags["fallback"],
                )
            )
    return Registry(
        meta=RegistryMeta(seed=seed, generator_version=GENERATOR_VERSION, disclaimer=DISCLAIMER),
        entities=entities,
        items=items,
    )
