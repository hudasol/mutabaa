"""Definition Card: the schema, the validator, the examples and the command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline import card
from pipeline.__main__ import main
from pipeline.io import ROOT

CASES = json.loads((ROOT / "data" / "golden" / "card_cases.json").read_text(encoding="utf-8"))
EXAMPLES = sorted((ROOT / "data" / "examples" / "definition_cards").glob("*.json"))


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_golden_cases(case):
    parsed, errors = card.validate(json.dumps(case["card"]))
    assert (parsed is not None) == case["valid"]
    assert (errors == []) == case["valid"]


def test_examples_are_valid_and_synthetic():
    assert len(EXAMPLES) >= 3
    for p in EXAMPLES:
        parsed, errors = card.validate(p.read_text(encoding="utf-8"))
        assert errors == [] and parsed is not None and parsed.is_synthetic


def test_not_json_and_not_an_object():
    assert "not valid JSON" in card.validate("{")[1][0]
    assert card.validate("[]")[1] == ["a card is one JSON object"]


def test_command_validates_and_recomputes(capsys):
    assert main(["mutabaa", "definition", "validate", str(EXAMPLES[0])]) == 0
    out = capsys.readouterr().out
    assert out.startswith("VALID") and "SYNTHETIC" in out and "%" in out


def test_command_rejects_a_bad_card(tmp_path: Path, capsys):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"title": "x"}), encoding="utf-8")
    assert main(["mutabaa", "definition", "validate", str(p)]) == 1
    assert "INVALID" in capsys.readouterr().out
    assert main(["mutabaa", "definition", "validate", str(tmp_path / "none.json")]) == 2


def test_the_share_matches_the_lab_calculation():
    from pipeline.__main__ import SYNTH
    from pipeline.schemas import Registry
    from pipeline.sensitivity import share

    reg = Registry.model_validate(json.loads((SYNTH / "registry.json").read_text(encoding="utf-8")))
    parsed, _ = card.validate(EXAMPLES[0].read_text(encoding="utf-8"))
    assert parsed is not None
    s = share(reg, parsed.definition)
    assert card.apply(parsed, reg)["share"] == (None if s is None else round(s, 6))
