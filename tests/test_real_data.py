import copy
import json
from datetime import date

import pytest

from pipeline.io import REAL, load_real
from pipeline.score import score
from pipeline.status import status
from pipeline.validate import validate


@pytest.fixture(scope="module")
def d():
    return load_real()


@pytest.fixture(scope="module")
def src(d):
    return {s.id: s for s in d.sources}


def by_id(items):
    return {x.id: x for x in items}


def test_dataset_validates():
    errors, _ = validate()
    assert errors == []


def test_every_commitment_has_a_status_and_score(d, src):
    for c in d.commitments:
        assert status(c, d.evidence, src).commitment_id == c.id
        assert 0 <= score(c).ratio <= 1


def test_headline_target_is_not_checkable_on_its_face(d):
    r = score(by_id(d.commitments)["C01"])
    assert r.band == "not-yet-checkable"
    assert "unit_defined" in r.missing and "terms_defined" in r.missing


def test_media_only_evidence_never_moves_status(d, src):
    c = by_id(d.commitments)["C03"]
    r = status(c, d.evidence, src)
    assert r.status == "no-public-evidence"
    assert r.excluded_evidence_ids == ["E07"]


def test_default_status_is_neutral_not_failed(d, src):
    c = by_id(d.commitments)["C13"]
    assert status(c, d.evidence, src).status == "no-public-evidence"


def test_projections_and_vision_are_not_graded(d, src):
    for cid in ("C08", "C17", "C18", "C23"):
        assert status(by_id(d.commitments)[cid], d.evidence, src).status == "not-checkable"


def test_unit_mismatch_is_flagged_not_converted(d, src):
    r = status(by_id(d.commitments)["C14"], d.evidence, src)
    assert r.status == "activity-reported"
    assert r.unit_mismatch is True
    assert r.progress_ratio is None


def test_matching_units_give_a_ratio(d, src):
    c = by_id(d.commitments)["C19"]
    r = status(c, d.evidence, src)
    assert r.unit_mismatch is False
    assert r.status == "activity-reported"  # target has no number, so no ratio


def test_ratio_when_unit_and_number_match(d, src):
    c = by_id(d.commitments)["C14"].model_copy(update={"unit": "use-cases"})
    r = status(c, d.evidence, src)
    assert r.status == "milestone-reported"
    assert r.progress_ratio == 0.5
    assert r.progress_as_of == date(2025, 9, 30)
    assert r.self_reported_only is True


def test_hash_tamper_is_caught(d, tmp_path, monkeypatch):
    bad = copy.deepcopy(d)
    bad.sources[0].content_hash = "0" * 64
    errors, _ = validate(bad)
    assert any("stale" in e for e in errors)


def test_anchor_tamper_is_caught(d):
    bad = copy.deepcopy(d)
    bad.commitments[0].anchors[0].text = "a phrase that is nowhere in the notes"
    errors, _ = validate(bad)
    assert any("anchor not found" in e for e in errors)


def test_media_cannot_claim_official_confirmation(d):
    bad = copy.deepcopy(d)
    e = by_id(bad.evidence)["E07"]
    e.corroboration = "official-confirmed"
    errors, _ = validate(bad)
    assert any("official-confirmed" in x for x in errors)


def test_json_files_are_utf8_arabic():
    raw = json.loads((REAL / "commitments.json").read_text(encoding="utf-8"))
    assert all(any("؀" <= ch <= "ۿ" for ch in r["title_ar"]) for r in raw)


def test_site_payload_is_up_to_date(tmp_path):
    """site/src/data/real.json is generated; it must match what the pipeline produces now."""
    import subprocess
    import sys

    from pipeline.io import ROOT

    p = ROOT / "site" / "src" / "data" / "real.json"
    before = p.read_text(encoding="utf-8")
    subprocess.run(
        [sys.executable, "-m", "pipeline", "build"], check=True, capture_output=True, cwd=ROOT
    )
    assert p.read_text(encoding="utf-8") == before, "run `python -m pipeline build` and commit"
