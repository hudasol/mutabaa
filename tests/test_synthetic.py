import json

import pytest
from pydantic import ValidationError

from pipeline.__main__ import GOLDEN, SYNTH
from pipeline.schemas import Definition, Registry
from pipeline.sensitivity import all_definitions, share, sweep
from pipeline.synth import generate


def test_generation_is_deterministic():
    assert generate().model_dump() == generate().model_dump()


def test_different_seed_differs():
    assert generate(seed=1).model_dump() != generate().model_dump()


def test_everything_is_labelled_synthetic():
    reg = generate()
    assert reg.meta.is_synthetic and "SYNTHETIC" in reg.meta.disclaimer
    assert all(i.is_synthetic for i in reg.items) and all(e.is_synthetic for e in reg.entities)


def test_schema_refuses_unlabelled_item():
    item = generate().items[0].model_dump()
    item["is_synthetic"] = False
    from pipeline.schemas import ServiceItem

    with pytest.raises(ValidationError):
        ServiceItem(**item)


def test_committed_registry_matches_generator():
    committed = Registry.model_validate_json((SYNTH / "registry.json").read_text())
    assert committed.model_dump() == generate().model_dump()


def test_committed_golden_matches_engine():
    reg = generate()
    assert json.loads((GOLDEN / "sensitivity.json").read_text()) == sweep(reg)


def test_there_are_72_definitions():
    assert len(all_definitions()) == 72


def test_stricter_definition_never_raises_the_share():
    reg = generate()
    for unit in ("services", "transactions"):
        loose = share(
            reg, Definition(unit=unit, scope="all-services", threshold=2, guardrails="none")
        )
        tight = share(
            reg, Definition(unit=unit, scope="all-services", threshold=4, guardrails="required")
        )
        assert tight <= loose


def test_definition_choice_moves_the_headline_a_lot():
    rows = [r["share"] for r in sweep(generate()) if r["share"] is not None]
    assert max(rows) - min(rows) > 0.5
