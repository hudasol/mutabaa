"""The commitment linter: deterministic, offline, and it never invents a value."""

from __future__ import annotations

import json
import re

import pytest

from pipeline.__main__ import golden_files
from pipeline.io import ROOT
from pipeline.lint import lint, normalise, parse

GOLDEN = ROOT / "data" / "golden"


def test_golden_outputs_are_current():
    assert (GOLDEN / "lint_outputs.json").read_text(encoding="utf-8") == golden_files()["lint_outputs.json"]


def test_same_input_gives_same_output():
    text = "The Example Office will reach 70% of services by 31 December 2027, measured by the annual report."
    assert lint(text) == lint(text)


def test_nothing_is_invented():
    r = lint("We will improve digital services soon.")
    f = r["found"]
    assert f["target_number"] is None and f["unit"] is None and f["owner"] is None
    assert r["before"]["ratio"] == 0.0
    assert {q["check"] for q in r["questions"]} >= {"numeric_target", "dated_deadline", "owner_named"}


def test_every_found_value_comes_from_the_text():
    text = "The Example Office will reach 70% of services by 31 December 2027, measured by the annual report."
    n = normalise(text).lower()
    f = lint(text)["found"]
    for key in ("owner", "measurement_source", "deadline_text"):
        assert f[key] is None or f[key].lower() in n
    assert f["target_number"] == 70.0


def test_start_dates_are_not_deadlines():
    assert parse("Since 2019 the office has run the programme.").deadline_precision == "none"
    assert parse("Reach 40% by 2028, announced in 2024.").deadline_text == "2028"


def test_arabic_digits_and_percent_are_read():
    p = parse("إنجاز ٨٠٪ من الخدمات بحلول ٢٠٢٧")
    assert p.target_number == 80.0 and p.deadline_text == "2027"


def test_filling_a_field_raises_the_score_and_never_lowers_it():
    r = lint("We will improve digital services soon.", fields={"owner": "The Example Office"})
    assert r["after"]["ratio"] > r["before"]["ratio"]
    assert r["after_found"]["owner"] == "The Example Office"
    assert r["found"]["owner"] is None


def test_unknown_or_empty_fields_change_nothing():
    r = lint("Reach 40% of services online by 2028.", fields={"owner": "", "unit": None})
    assert r["after"] is None


def test_long_text_is_cut():
    assert len(lint("a " * 5000)["text"]) <= 4000


@pytest.mark.parametrize("case", json.loads((GOLDEN / "lint_inputs.json").read_text(encoding="utf-8")))
def test_golden_inputs_run(case):
    r = lint(case["text"], case.get("kind", "target"), case.get("fields"))
    assert 0.0 <= r["before"]["ratio"] <= 1.0
    assert not re.search(r"\s{2,}", r["text"])


def test_cli_prints_found_fields_and_questions(capsys):
    from pipeline.__main__ import main

    assert main(["mutabaa", "lint", "Reach 40% of services online by 2028."]) == 0
    out = capsys.readouterr().out
    assert "Target number: 40.0" in out and "Owner: (not stated)" in out and "Questions to answer:" in out


def test_cli_min_ratio_sets_the_exit_code(capsys):
    from pipeline.__main__ import main

    assert main(["mutabaa", "lint", "We will improve things.", "--min-ratio", "0.5"]) == 1
    capsys.readouterr()
    assert main(["mutabaa", "lint", ""]) == 2
    assert main(["mutabaa", "lint", "--file", "no/such/file.txt"]) == 2


def test_cli_json_includes_the_after_score(capsys):
    from pipeline.__main__ import main

    main(["mutabaa", "lint", "We will improve things.", "--owner", "The Example Office", "--format", "json"])
    res = json.loads(capsys.readouterr().out)
    assert res["after"]["ratio"] > res["before"]["ratio"]


def test_lint_rules_are_frozen_for_e9():
    import hashlib

    digest = hashlib.sha256((ROOT / "data" / "config" / "lint_rules.json").read_bytes()).hexdigest()
    frozen = (ROOT / "tests" / "frozen" / "lint_rules_v1_8_0.sha256").read_text(encoding="utf-8").strip()
    assert digest == frozen, "rules changed after E9 was registered; label any new version exploratory"
