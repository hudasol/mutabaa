"""The command line, run in process.

Output files go to a temporary folder and are compared with the repository.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import pipeline.__main__ as cli
from pipeline import facts
from pipeline.diff import diff, load_current

ROOT = Path(__file__).resolve().parent.parent


def run(*args: str) -> int:
    return cli.main(["pipeline", *args])


def test_unknown_command_prints_usage(capsys):
    assert run("nope") == 2
    assert "validate" in capsys.readouterr().out


def test_validate_passes_on_committed_data(capsys):
    assert run("validate") == 0
    assert "0 error(s)" in capsys.readouterr().out


def test_synth_reproduces_committed_registry_and_golden_file(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "SYNTH", tmp_path / "synthetic")
    monkeypatch.setattr(cli, "GOLDEN", tmp_path / "golden")
    assert run("synth") == 0
    for sub, name in (("synthetic", "registry.json"), ("golden", "sensitivity.json")):
        assert (tmp_path / sub / name).read_text(encoding="utf-8") == (
            ROOT / "data" / sub / name
        ).read_text(encoding="utf-8")


def test_build_reproduces_committed_payload(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    assert run("build") == 0
    built = (tmp_path / "site" / "src" / "data" / "real.json").read_bytes()
    assert built == (ROOT / "site" / "src" / "data" / "real.json").read_bytes()


def test_rehash_keeps_committed_hashes(tmp_path, monkeypatch):
    shutil.copy(ROOT / "data" / "real" / "sources.json", tmp_path / "sources.json")
    monkeypatch.setattr(cli, "REAL", tmp_path)
    assert run("rehash") == 0
    assert json.loads((tmp_path / "sources.json").read_text(encoding="utf-8")) == json.loads(
        (ROOT / "data" / "real" / "sources.json").read_text(encoding="utf-8")
    )


def test_analyse_writes_one_file_per_analysis(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ANALYSIS", tmp_path)
    monkeypatch.setattr(cli, "compute_analysis", lambda d: {"robustness": {"x": 1}, "agreement": {"y": 2}})
    assert run("analyse") == 0
    assert json.loads((tmp_path / "robustness.json").read_text(encoding="utf-8")) == {"x": 1}
    assert (tmp_path / "agreement.json").exists()


def test_facts_report_and_schema_match_committed_files(tmp_path, monkeypatch):
    monkeypatch.setattr(facts, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(cli, "REPORTS", {"EVALUATION.md": tmp_path / "EVALUATION.md"})
    assert run("facts") == 0
    assert run("report") == 0
    assert (tmp_path / "results" / "facts.json").read_text(encoding="utf-8") == (
        ROOT / "results" / "facts.json"
    ).read_text(encoding="utf-8")
    assert (tmp_path / "EVALUATION.md").read_text(encoding="utf-8") == (
        ROOT / "docs" / "EVALUATION.md"
    ).read_text(encoding="utf-8")
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    assert run("schema") == 0
    for p in (ROOT / "schema").glob("*.json"):
        assert (tmp_path / "schema" / p.name).read_text(encoding="utf-8") == p.read_text(encoding="utf-8")


def test_diff_against_head_runs(capsys):
    if shutil.which("git") is None:
        pytest.skip("git is not available")
    assert run("diff", "HEAD") == 0
    assert capsys.readouterr().out.strip()


def test_verify_live_writes_results_without_network(tmp_path, monkeypatch, capsys):
    (tmp_path / "verification.json").write_text(json.dumps({"results": {"S99": {"result": "verified"}}}))
    monkeypatch.setattr(cli, "REAL", tmp_path)

    def fake(sources, only=None):
        assert only == {"S01"}
        return {"run_at": "t", "results": {"S01": {"result": "verified", "missing": [], "unexpected": []}}}

    monkeypatch.setattr(cli, "run_verify", fake)
    assert run("verify-live", "--only", "S01", "--write") == 0
    out = json.loads((tmp_path / "verification.json").read_text(encoding="utf-8"))
    assert set(out["results"]) == {"S01", "S99"} and out["run_at"] == "t"

    def failing(sources, only=None):
        return {"results": {"S01": {"result": "failed", "missing": ["x"], "unexpected": []}}}

    monkeypatch.setattr(cli, "run_verify", failing)
    assert run("verify-live") == 1
    assert "failed" in capsys.readouterr().out


def test_diff_reports_a_changed_target_value():
    old = load_current()
    new = json.loads(json.dumps(old))
    new["commitments"][0]["target_number"] = 12345.0
    new["commitments"][1]["target_value"] = "a new wording"
    lines = diff(old, new)
    assert any("target_number" in x for x in lines)
    assert any("target_value" in x for x in lines)


def test_diff_reports_added_and_removed_commitments():
    old = load_current()
    new = json.loads(json.dumps(old))
    gone = new["commitments"].pop(0)
    new["commitments"].append({**gone, "id": "C99"})
    lines = diff(old, new)
    assert any(x.startswith("+ C99") for x in lines)
    assert any(x.startswith(f"- {gone['id']}") for x in lines)
