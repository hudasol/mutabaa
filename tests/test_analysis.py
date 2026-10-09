import json

from pipeline import agreement, calibration, robustness
from pipeline.__main__ import ANALYSIS
from pipeline.io import load_real
from pipeline.stats import bootstrap_ci, cohen_kappa, quantile, spearman


def test_kappa_known_values():
    assert cohen_kappa([True, True, False, False], [True, True, False, False]) == 1.0
    assert abs(cohen_kappa([True, True, False, False], [True, False, True, False])) < 1e-9


def test_spearman_monotone_and_ties():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0
    assert spearman([1, 1, 1], [1, 2, 3]) is None


def test_quantile_and_bootstrap_are_deterministic():
    assert quantile([1, 2, 3, 4, 5], 0.5) == 3
    f = lambda ix: sum(ix) / len(ix)  # noqa: E731
    assert bootstrap_ci(10, f) == bootstrap_ci(10, f)


def test_effects_are_shares_of_variance():
    from pipeline.sensitivity import sweep
    from pipeline.synth import generate

    eff = robustness.first_order_effects(sweep(generate()))
    assert all(0 <= v <= 1 for v in eff.values()) and sum(eff.values()) <= 1.0 + 1e-9


def test_calibration_and_agreement_match_committed_files():
    d = load_real()
    for name, mod in (("calibration", calibration), ("agreement", agreement)):
        got = json.loads(json.dumps(mod.run(d.commitments), sort_keys=True))
        assert got == json.loads((ANALYSIS / f"{name}.json").read_text("utf-8"))


def test_robustness_matches_committed_file():
    got = json.loads(json.dumps(robustness.run(), sort_keys=True))
    assert got == json.loads((ANALYSIS / "robustness.json").read_text("utf-8"))


def test_band_changes_are_bounded_by_commitment_count():
    r = calibration.run(load_real().commitments)
    assert 0 <= r["bands"]["max_changed"] <= r["bands"]["n"]


def test_axes_config_matches_code():
    from typing import get_args

    from pipeline.io import ROOT
    from pipeline.schemas import Guardrails, Scope, Threshold, Unit

    cfg = json.loads((ROOT / "data" / "config" / "definition_axes.json").read_text("utf-8"))
    assert set(cfg["unit"]) == set(get_args(Unit))
    assert set(cfg["scope"]) == set(get_args(Scope))
    assert set(cfg["threshold"]) == {str(x) for x in get_args(Threshold)}
    assert set(cfg["guardrails"]) == set(get_args(Guardrails))
