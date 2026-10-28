"""E5 and E6: unit tests for the helpers, and the committed results against a fresh run."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from pipeline import evaluate_real as er
from pipeline import status as status_module
from pipeline.io import load_real

ROOT = Path(__file__).resolve().parent.parent


def test_note_units_join_continuations_and_drop_short_bullets():
    text = (
        "# Title\n\nintro\n\n- first bullet has five words\n  and a continuation\n"
        "- too short\n- third one here ok\n"
    )
    assert er.note_units(text) == [
        "first bullet has five words and a continuation",
        "third one here ok",
    ]


def test_note_units_ignore_headers_and_blank_separated_text():
    assert er.note_units("# h\n\nplain paragraph text here\n\n- a b c d\n\nmore text") == ["a b c d"]


@pytest.mark.parametrize(
    ("text", "flags"),
    [
        ("transform 50% of services within two years", {"x1": True, "x2": True, "x3": True, "x4": True}),
        ("a 13 billion investment", {"x1": True, "x2": True, "x3": False, "x4": False}),
        ("the strategy runs to 2027 with 200 solutions", {"x1": True, "x2": False, "x3": False, "x4": False}),
        ("a programme will be launched", {"x1": False, "x2": False, "x3": False, "x4": True}),
        ("targets and plans are described", {"x1": False, "x2": False, "x3": False, "x4": False}),
    ],
)
def test_extractor_rules(text, flags):
    for name, want in flags.items():
        assert er.EXTRACTORS[name](text) is want, name
    assert er.x0(text) is True


def test_every_experiment_has_predictions_marked_hit_or_miss():
    for fn in (er.e5, er.e6):
        out = fn()
        assert out["predictions"] and all(v["result"] in ("HIT", "MISS") for v in out["predictions"].values())
        assert all(set(v) == {"value", "format"} for v in out["facts"].values())


@pytest.mark.parametrize("name", ["e5", "e6"])
def test_committed_results_equal_a_fresh_run(name):
    stored = json.loads((ROOT / "results" / f"{name}.json").read_text(encoding="utf-8"))
    fresh = getattr(er, name)()
    assert stored == json.loads(json.dumps(fresh))


def test_invariants_hold_for_the_real_engine():
    d = load_real()
    as_of = max(s.retrieved for s in d.sources)
    bad = er.check_invariants(status_module.status, d, as_of)
    assert not any(bad.values()), bad


def test_a_broken_engine_is_caught():
    """If media evidence counted, the media invariant must fail."""
    d = load_real()
    as_of = max(s.retrieved for s in d.sources)
    with er._patched(eligible=lambda e, s: True):
        bad = er.check_invariants(lambda c, ev, s, when: status_module.status(c, ev, s, when), d, as_of)
    assert bad["I2"]


def test_all_five_mutants_are_killed_by_some_invariant():
    out = er.e6()
    assert all(m["violated"] for m in out["mutants"].values()), out["mutants"]


def test_perturbations_never_reach_disk():
    d = load_real()
    before = (ROOT / "data" / "real" / "evidence.json").read_bytes()
    er.check_invariants(status_module.status, d, date(2026, 10, 10))
    assert (ROOT / "data" / "real" / "evidence.json").read_bytes() == before
