"""Each integrity rule in pipeline/validate.py, triggered by one deliberate mistake."""

from __future__ import annotations

import copy
from datetime import date

import pytest

from pipeline.io import load_real
from pipeline.schemas import SearchEntry
from pipeline.validate import validate


@pytest.fixture(scope="module")
def base():
    return load_real()


def errors_after(base, edit) -> list[str]:
    d = copy.deepcopy(base)
    edit(d)
    return validate(d)[0]


def by(items, i):
    return next(x for x in items if x.id == i)


CASES = [
    ("duplicate commitment id", lambda d: d.commitments.append(copy.deepcopy(d.commitments[0]))),
    ("extract file", lambda d: setattr(d.sources[0], "extract_file", "data/real/extracts/missing.md")),
    ("published after retrieved", lambda d: setattr(d.sources[0], "published", date(2099, 1, 1))),
    ("unknown source S77", lambda d: d.commitments[0].source_ids.append("S77")),
    ("not in source_ids", lambda d: setattr(d.commitments[0].anchors[0], "source_id", "S14")),
    ("deadline precedes announcement",
     lambda d: [setattr(c, "announced", date(2099, 1, 1)) for c in d.commitments if c.deadline][:1]),
    ("unknown commitment C99", lambda d: d.evidence[0].commitment_ids.append("C99")),
    ("official source marked", lambda d: setattr(
        next(e for e in d.evidence if by(d.sources, e.source_id).kind != "secondary-media"),
        "corroboration", "single-source")),
    ("as_of after retrieval", lambda d: setattr(
        next(e for e in d.evidence if e.as_of), "as_of", date(2099, 1, 1))),
    ("needs value and unit", lambda d: setattr(
        next(e for e in d.evidence if e.kind == "quantified-progress"), "value", None)),
    ("unknown commitment C98", lambda d: d.claims[0].commitment_ids.append("C98")),
    ("is not official", lambda d: d.claims[0].official_sources_checked.append(
        next(s.id for s in d.sources if s.kind == "secondary-media"))),
    ("duplicate search id", lambda d: d.searches.append(copy.deepcopy(d.searches[0]))),
    ("unknown commitment C97", lambda d: d.searches[0].commitment_ids.append("C97")),
    ("unknown source S76", lambda d: d.searches[0].found_source_ids.append("S76")),
    ("no source is listed", lambda d: d.searches.append(SearchEntry(
        id="Q99", searched_on=date(2026, 10, 1), tool="WebSearch", query="q", commitment_ids=["C01"],
        outcome="progress-found"))),
    ("verification: unknown source",
     lambda d: d.verification["results"].update({"S75": {"result": "verified"}})),
    ("live verification failed", lambda d: d.verification["results"].update(
        {"S01": {"result": "failed", "missing": ["x"], "unexpected": []}})),
    ("only from AI-assisted", lambda d: [setattr(s, "ai_assisted", True) for s in d.sources]),
]


@pytest.mark.parametrize("expected,edit", CASES, ids=[c[0] for c in CASES])
def test_each_rule_fires(base, expected, edit):
    errs = errors_after(base, edit)
    assert any(expected in e for e in errs), errs


def test_unverified_source_is_a_warning(base):
    d = copy.deepcopy(base)
    d.verification["results"].pop("S01")
    errors, warnings = validate(d)
    assert errors == [] and any("S01: not yet verified" in w for w in warnings)
