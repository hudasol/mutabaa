"""Generator B follows the specification in PREREGISTRATION.md (E2)."""

from __future__ import annotations

import statistics

from pipeline.schemas import Registry
from pipeline.synth import SECTORS
from pipeline.synth_b import PROFILE_MEANS, generate_b


def test_deterministic_for_a_seed():
    a = generate_b(seed=3, n_entities=8, profile="mid").model_dump()
    b = generate_b(seed=3, n_entities=8, profile="mid").model_dump()
    assert a == b
    assert a != generate_b(seed=4, n_entities=8, profile="mid").model_dump()


def test_records_are_valid_and_synthetic():
    reg = generate_b(seed=1, n_entities=16, profile="high")
    Registry.model_validate(reg.model_dump())
    assert reg.meta.is_synthetic and all(i.is_synthetic for i in reg.items)
    assert [e.sector for e in reg.entities[:8]] == SECTORS
    assert reg.entities[0].name.startswith("Synthetic ") and " Office " in reg.entities[0].name


def test_entity_sizes_follow_the_heavy_tailed_rule():
    reg = generate_b(seed=2, n_entities=32, profile="mid")
    sizes = [sum(1 for i in reg.items if i.entity_id == e.id) for e in reg.entities]
    assert min(sizes) >= 10 and max(sizes) <= 120


def test_profiles_shift_maturity():
    means = {p: statistics.mean(i.maturity for i in generate_b(seed=5, n_entities=16, profile=p).items)
             for p in PROFILE_MEANS}
    assert means["low"] < means["mid"] < means["high"]


def test_guardrail_flags_are_correlated_with_maturity():
    items = [i for s in range(1, 6) for i in generate_b(seed=s, n_entities=16, profile="mid").items]
    hi = [i for i in items if i.maturity >= 3]
    lo = [i for i in items if i.maturity <= 1]
    rate = lambda xs: statistics.mean(x.oversight and x.audit_trail for x in xs)  # noqa: E731
    assert rate(hi) > rate(lo)


def test_operations_are_internal_and_often_have_no_volume():
    items = [i for i in generate_b(seed=7, n_entities=32, profile="mid").items if i.kind == "operation"]
    assert items and all(i.audience == "internal" for i in items)
    assert any(i.annual_transactions == 0 for i in items)
