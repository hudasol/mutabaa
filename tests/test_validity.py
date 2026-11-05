"""The validity study code: the frozen population, the freeze file and the permutation test."""

from __future__ import annotations

import json
from pathlib import Path

from pipeline import validity
from pipeline.io import load_real
from pipeline.score import score

ROOT = Path(__file__).resolve().parent.parent


def test_population_is_the_registered_set_of_dated_commitments_before_the_cutoff():
    ids = validity.population()
    d = load_real()
    assert ids == sorted(ids)
    assert len(ids) == 36
    by_id = {c.id: c for c in d.commitments}
    assert all(by_id[i].deadline is not None and by_id[i].deadline < validity.CUTOFF for i in ids)
    assert all(c.id in ids for c in d.commitments if c.deadline and c.deadline < validity.CUTOFF)


def test_the_committed_freeze_equals_a_recomputation():
    """The scores were frozen before outcomes were read; rerunning must not change them."""
    committed = json.loads((ROOT / "data/e8/frozen_scores.json").read_text(encoding="utf-8"))
    assert validity.freeze() == committed


def test_frozen_scores_equal_the_live_scoring_function():
    d = {c.id: c for c in load_real().commitments}
    frozen = json.loads((ROOT / "data/e8/frozen_scores.json").read_text(encoding="utf-8"))["commitments"]
    for cid, row in frozen.items():
        assert row["score"] == score(d[cid]).ratio


def test_permutation_p_is_small_for_a_perfect_separation_and_large_for_none():
    scores = [float(i) for i in range(12)]
    labels = [False] * 6 + [True] * 6
    low = validity.permutation_p(scores, labels, 1.0)
    assert low < 0.01
    mixed = [True, False] * 6
    high = validity.permutation_p(scores, mixed, 0.5)
    assert high > 0.4
    assert validity.permutation_p(scores, labels, 1.0) == low


def test_e8_reports_the_registered_population_and_is_repeatable():
    a = validity.e8()
    b = validity.e8()
    assert a == b
    assert a["n"] == 36
