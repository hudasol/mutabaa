"""Numbers in documents must agree with the files the code produces.

A cited number is written as <!-- fact:KEY -->TEXT<!-- /fact -->. KEY is a key of results/facts.json,
which `python -m pipeline facts` computes from the payload, data/analysis/ and results/.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from pipeline import facts

ROOT = Path(__file__).resolve().parent.parent
MARK = re.compile(r"<!-- fact:([\w.\-]+) -->(.*?)<!-- /fact -->")
DOCS = sorted(
    [p for p in (ROOT / "README.md", ROOT / "PREREGISTRATION.md") if p.exists()]
    + list((ROOT / "docs").rglob("*.md")),
    key=lambda p: p.as_posix(),
)
MUST_CITE = ["README.md", "docs/EVALUATION.md", "docs/METHODOLOGY.md", "docs/LIMITATIONS.md"]
TEST_COUNT = re.compile(r"\b\d+\s+(Python|unit|site|browser|vitest|pytest|Playwright|e2e)\s+tests\b", re.I)


@pytest.fixture(scope="module")
def fresh() -> dict:
    return facts.compute()


def test_facts_file_is_up_to_date(fresh):
    stored = json.loads((ROOT / "results" / "facts.json").read_text(encoding="utf-8"))
    assert stored == json.loads(facts.dumps(fresh)), "run `python -m pipeline facts` and commit"


@pytest.mark.parametrize("path", DOCS, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_marked_numbers_match_facts(path: Path, fresh):
    text = path.read_text(encoding="utf-8")
    bad = []
    for key, shown in MARK.findall(text):
        if key not in fresh:
            bad.append(f"unknown fact {key!r}")
        elif shown != fresh[key]["text"]:
            bad.append(f"{key}: document shows {shown!r}, source gives {fresh[key]['text']!r}")
    assert bad == [], "\n".join(bad)


@pytest.mark.parametrize("rel", MUST_CITE)
def test_key_documents_cite_facts(rel):
    assert MARK.search((ROOT / rel).read_text(encoding="utf-8")), f"{rel} has no marked numbers"


@pytest.mark.parametrize("path", DOCS, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_no_hard_coded_test_counts(path: Path):
    hits = TEST_COUNT.findall(path.read_text(encoding="utf-8"))
    assert not hits, f"test counts go stale; remove them: {hits}"


def test_a_changed_analysis_value_is_detected(monkeypatch, fresh):
    """Simulate an edit to data/analysis/robustness.json and check that the facts change with it."""
    real = facts._load

    def edited(path):
        d = real(path)
        if path.name == "robustness.json":
            d = {**d, "flip_rate": round(d["flip_rate"] - 0.11, 4)}
        return d

    monkeypatch.setattr(facts, "_load", edited)
    changed = facts.compute()
    assert changed["robustness.flip_rate"]["text"] != fresh["robustness.flip_rate"]["text"]


def test_rendered_reports_are_up_to_date():
    from pipeline.__main__ import render_reports

    for out, text in render_reports().items():
        assert out.read_text(encoding="utf-8") == text, f"run `python -m pipeline report` ({out.name})"


def test_render_marks_facts_and_rejects_unknown_keys():
    from pipeline.render import render

    fx = {"a.b": {"text": "80%"}}
    assert render("x {a.b} y", fx) == "x <!-- fact:a.b -->80%<!-- /fact --> y"
    assert render("no placeholder {here}", fx) == "no placeholder {here}"
    with pytest.raises(KeyError):
        render("{a.c}", fx)


def test_formats():
    assert facts.fmt(0.8, "pct") == "80%"
    assert facts.fmt(1234, "int") == "1,234"
    assert facts.fmt(0.9361, "f2") == "0.94"
    assert facts.fmt(["C01", "C02"], "list") == "C01, C02"
    with pytest.raises(ValueError):
        facts.fmt(1, "nope")


def test_refresh_rewrites_stale_values_and_is_idempotent():
    from pipeline.render import refresh

    fx = {"a.b": {"text": "80%"}}
    stale = "x <!-- fact:a.b -->12%<!-- /fact --> y <!-- fact:a.b -->80%<!-- /fact -->"
    fixed = refresh(stale, fx)
    assert fixed == "x <!-- fact:a.b -->80%<!-- /fact --> y <!-- fact:a.b -->80%<!-- /fact -->"
    assert refresh(fixed, fx) == fixed
    with pytest.raises(KeyError):
        refresh("<!-- fact:zz -->1<!-- /fact -->", fx)


def test_sync_docs_leaves_committed_documents_unchanged(capsys):
    from pipeline.__main__ import cmd_sync_docs

    assert cmd_sync_docs() == 0
    assert "0 document(s) updated" in capsys.readouterr().out
