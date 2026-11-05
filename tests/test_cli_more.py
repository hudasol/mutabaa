"""Commands added in v1.8.0: lint, definition validate, monitor, schema, e8-freeze and the fact commands."""

import json
from pathlib import Path

import pytest

import pipeline.__main__ as cli
from pipeline.__main__ import main
from tests.test_monitor import PAGES, _report, _sources

ROOT = Path(__file__).resolve().parent.parent
CARD = ROOT / "data/examples/definition_cards/example1.json"


def run(capsys, *args):
    code = main(["mutabaa", *args])
    return code, capsys.readouterr()


def test_lint_text_names_what_is_missing(capsys):
    code, out = run(capsys, "lint", "Improve digital services.", "--lang", "both")
    assert code == 0 and "Target number: (not stated)" in out.out and "Questions to answer" in out.out


def test_lint_json_with_answers_rescores(capsys):
    code, out = run(capsys, "lint", "Improve digital services.", "--format", "json", "--number", "50",
                    "--unit", "services", "--deadline", "2028-12-31", "--owner", "Office")
    res = json.loads(out.out)
    assert code == 0 and res["after"]["ratio"] > res["before"]["ratio"]


def test_lint_min_ratio_sets_exit_code_and_file_input(capsys, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("Improve digital services.", encoding="utf-8")
    assert run(capsys, "lint", "--file", str(f), "--min-ratio", "0.9")[0] == 1
    assert run(capsys, "lint", "--file", str(tmp_path / "missing.txt"))[0] == 2
    assert run(capsys, "lint", "   ")[0] == 2


def test_definition_validate_valid_missing_and_invalid(capsys, tmp_path):
    code, out = run(capsys, "definition", "validate", str(CARD))
    assert code == 0 and "VALID" in out.out and "SYNTHETIC" in out.out
    assert run(capsys, "definition", "validate", str(tmp_path / "none.json"))[0] == 2
    bad = tmp_path / "bad.json"
    bad.write_text("{}", encoding="utf-8")
    code, out = run(capsys, "definition", "validate", str(bad))
    assert code == 1 and "INVALID" in out.out


def test_monitor_writes_a_dated_report_and_sets_the_output_flag(capsys, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "run_verify", lambda sources: _report(PAGES))
    monkeypatch.setattr(cli, "load_real", lambda: _Stub())
    gh = tmp_path / "gh_out"
    monkeypatch.setenv("GITHUB_OUTPUT", str(gh))
    code, out = run(capsys, "monitor", "--out", str(tmp_path / "m"))
    assert code == 0 and "attention=" in out.out
    assert any(p.name.startswith("drift-") and p.suffix == ".md" for p in (tmp_path / "m").iterdir())
    assert "attention=" in gh.read_text(encoding="utf-8") and "date=" in gh.read_text(encoding="utf-8")


class _Stub:
    sources = _sources()
    verification = _report(PAGES)


def test_schema_files_are_written(tmp_path):
    from pipeline import schema_export

    paths = schema_export.write(tmp_path / "s")
    assert paths and all(p.exists() for p in paths)
    assert any(p.name == "definition_card.schema.json" for p in paths)


def test_environment_records_versions():
    env = cli.environment()
    assert env["python"] and "packages" in env


@pytest.mark.parametrize("cmd", ["facts"])
def test_facts_command_runs(capsys, cmd):
    assert run(capsys, cmd)[0] == 0
