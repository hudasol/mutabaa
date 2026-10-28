import json

import pytest

from pipeline.__main__ import main

GOOD = "id,title,kind,owner,deadline,target_number,unit\nA1,Move half,target,Office,2027-12-31,50,services\n"
MIXED = GOOD + "A2,,target,,,,\n"


def run(capsys, *args):
    code = main(["mutabaa", *args])
    return code, capsys.readouterr()


@pytest.fixture
def good(tmp_path):
    p = tmp_path / "good.csv"
    p.write_text(GOOD, encoding="utf-8")
    return str(p)


@pytest.fixture
def mixed(tmp_path):
    p = tmp_path / "mixed.csv"
    p.write_text(MIXED, encoding="utf-8")
    return str(p)


def test_score_text(capsys, good):
    code, out = run(capsys, "score", good)
    assert code == 0 and "1 of 1 rows read" in out.out and "A1" in out.out


def test_score_json_has_summary_and_no_questions_by_default(capsys, good):
    code, out = run(capsys, "score", good, "--format", "json")
    data = json.loads(out.out)
    assert code == 0 and data["summary"]["accepted"] == 1
    assert "questions" not in data["commitments"][0]


def test_questions_command_lists_questions_in_both_languages(capsys, good):
    code, out = run(capsys, "questions", good, "--lang", "both")
    assert code == 0 and "Which dataset or report" in out.out and "ما مجموعة" in out.out


def test_csv_output_neutralises_formulas(capsys, tmp_path):
    p = tmp_path / "f.csv"
    p.write_text("id,title,kind\n1,=1+1,vision\n", encoding="utf-8")
    code, out = run(capsys, "score", str(p), "--format", "csv")
    assert code == 0 and "'=1+1" in out.out


def test_gates(capsys, good, mixed):
    assert run(capsys, "score", good, "--min-ratio", "0.99")[0] == 1
    assert run(capsys, "score", good, "--min-ratio", "0.1")[0] == 0
    assert run(capsys, "score", mixed)[0] == 0
    code, out = run(capsys, "score", mixed, "--strict")
    assert code == 1 and "problem(s)" in out.out


def test_unreadable_input_exits_two(capsys, tmp_path):
    assert run(capsys, "score", str(tmp_path / "missing.csv"))[0] == 2
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    code, out = run(capsys, "score", str(bad))
    assert code == 2 and "not valid JSON" in out.err
    empty = tmp_path / "empty.csv"
    empty.write_text("id,title\n1,a\n", encoding="utf-8")
    assert run(capsys, "score", str(empty))[0] == 2


def test_template_round_trips(capsys, tmp_path):
    code, out = run(capsys, "template")
    p = tmp_path / "t.csv"
    p.write_text(out.out, encoding="utf-8")
    assert code == 0 and run(capsys, "score", str(p), "--strict")[0] == 0


def test_no_command_prints_help(capsys):
    code, out = run(capsys)
    assert code == 2 and "usage: mutabaa" in out.out


def test_version(capsys):
    with pytest.raises(SystemExit) as e:
        main(["mutabaa", "--version"])
    assert e.value.code == 0 and "mutabaa" in capsys.readouterr().out
