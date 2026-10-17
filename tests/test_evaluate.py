"""Helpers used by the preregistered experiments, and the committed results against a fresh run."""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from pipeline import evaluate as ev
from pipeline.synth import generate

ROOT = Path(__file__).resolve().parent.parent


def test_auc_known_values():
    assert ev.auc([0.1, 0.2, 0.8, 0.9], [False, False, True, True]) == 1.0
    assert ev.auc([0.9, 0.8, 0.2, 0.1], [False, False, True, True]) == 0.0
    assert ev.auc([0.5, 0.5], [False, True]) == 0.5
    assert ev.auc([1, 2], [True, True]) is None


def test_auc_interval_contains_point_and_is_deterministic():
    s = [0.2, 0.4, 0.5, 0.6, 0.9, 0.3, 0.7, 0.8]
    y = [False, False, True, True, True, False, False, True]
    a = ev.auc_ci(s, y, reps=300)
    assert a == ev.auc_ci(s, y, reps=300)
    assert a[0] <= ev.auc(s, y) <= a[1]


def test_wilson_known_value():
    lo, hi = ev.wilson(22, 25)
    assert round(lo, 3) == 0.700 and round(hi, 3) == 0.958
    lo, hi = ev.wilson(25, 25)
    assert hi == pytest.approx(1.0) and lo < 0.9


def test_percentile_bootstrap_degenerates_at_all_successes():
    assert ev.percentile_boot(25, 25, random.Random(1), reps=100) == (1.0, 1.0)


def test_competition_ranks_share_ties():
    assert ev.competition_ranks({"a": 0.5, "b": 0.9, "c": 0.5, "d": 0.1}) == {"b": 1, "a": 2, "c": 2, "d": 4}


def test_rank_noise_is_deterministic_and_counts_consistently():
    reg = generate(seed=3, n_entities=8)
    r1, r2 = ev.rank_noise(reg, reps=40), ev.rank_noise(reg, reps=40)
    assert r1 == r2
    assert r1["exceed_noise"] == len(r1["exceed_ids"]) <= r1["entities"]
    assert all(r1["definition_range"][e] > r1["noise_width"][e] for e in r1["exceed_ids"])


def test_outcome_requires_eligible_official_evidence():
    from pipeline.io import load_real

    d = load_real()
    y = {c.id: ev.outcome(c, d) for c in d.commitments}
    linked = {cid for e in d.evidence for cid in e.commitment_ids}
    assert all(not y[c] for c in y if c not in linked)


@pytest.mark.parametrize("name", ["e1", "e3"])
def test_committed_results_equal_a_fresh_run(name):
    stored = json.loads((ROOT / "results" / f"{name}.json").read_text(encoding="utf-8"))
    assert stored == json.loads(json.dumps(ev.EXPERIMENTS[name]()))


@pytest.mark.parametrize("name", ["e2", "e4"])
def test_slow_results_are_present_and_complete(name):
    """E2 and E4 take longer; CI reruns them through `python -m pipeline evaluate` (see Makefile)."""
    stored = json.loads((ROOT / "results" / f"{name}.json").read_text(encoding="utf-8"))
    assert stored["predictions"] and all(
        v["result"] in ("HIT", "MISS") for v in stored["predictions"].values()
    )


def test_coverage_simulation_runs_small_and_is_deterministic():
    a = ev.coverage(0.88, seeds=range(1, 3), runs=10)
    assert a == ev.coverage(0.88, seeds=range(1, 3), runs=10)
    assert 0 <= a["bootstrap"]["coverage"] <= 1 and 0 <= a["wilson"]["coverage"] <= 1


def test_generator_study_runs_small(monkeypatch):
    monkeypatch.setattr(ev, "SIZES", (8,))
    out = ev._study(lambda prof, n, seed: ev.generate_b(seed=seed % 3 + 1, n_entities=n, profile=prof))
    assert out["registries"] == 3 * 60 and set(out["by_profile"]) == {"low", "mid", "high"}
    assert abs(sum(out["effects"].values())) <= 1.0 + 1e-9
