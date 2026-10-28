import json

import pytest

from pipeline import own


@pytest.mark.parametrize(
    ("text", "want"),
    [
        ("2027-12-31", "day"), ("31 Dec 2027", "day"), ("Dec 31, 2027", "day"), ("31/12/2027", "day"),
        ("2027-12", "month"), ("12/2027", "month"), ("Dec 2027", "month"), ("Q4 2027", "month"),
        ("2027", "year"), ("by 2027", "year"), ("end of 2027", "year"),
        ("soon", "relative"), ("2027-13-01", "relative"), ("", "none"),
    ],
)
def test_deadline_precision(text, want):
    assert own.deadline_precision(text) == want


def test_csv_quoted_newline_semicolon_and_bom():
    text = '﻿id;title;kind\r\n1;"a; b\nc";target\r\n2;plain;vision\r\n'
    headers, rows, cut = own.read_file("x.csv", text)
    assert headers == ["id", "title", "kind"] and not cut
    assert rows[0][1] == "a; b\nc" and len(rows) == 2


def test_csv_tab_and_escaped_quote():
    headers, rows, _ = own.read_file("x.tsv", 'id\ttitle\tkind\n1\t"say ""hi"""\ttarget\n')
    assert rows[0][1] == 'say "hi"'


def test_json_forms_and_list_values():
    arr = json.dumps([{"id": "1", "title": "t", "kind": "target", "undefined_terms": ["a", "b"]}])
    for text in (arr, json.dumps({"commitments": json.loads(arr)})):
        res = own.load("x.json", text)
        assert res.accepted == 1 and res.items[0].undefined_terms == ["a", "b"]
    with pytest.raises(ValueError):
        own.read_file("x.json", "{")
    with pytest.raises(ValueError):
        own.read_file("x.json", '{"a": 1}')


def test_conversion_rejects_and_reports():
    text = "id,title,kind,target_number\n1,a,target,5%\n1,b,target,\n2,,target,\n3,c,bogus,\n4,d,target,x\n"
    res = own.load("x.csv", text)
    assert res.accepted == 1 and res.rejected == 4 and res.duplicates == 1
    assert res.items[0].target_number == 5.0
    assert own.load("x.csv", "id,title\n1,a\n").errors == ["Missing columns: kind."]
    assert own.load("x.csv", "").errors


def test_synonyms_and_cell_escaping():
    assert own.map_columns(["Code", "Name", "Type"]) == {"id": 0, "title": 1, "kind": 2}
    assert own.csv_cell("=1+1") == '"\'=1+1"'
    assert own.csv_cell('a"b') == '"a""b"'


def test_row_cap(monkeypatch):
    monkeypatch.setattr(own, "MAX_ROWS", 2)
    _, rows, cut = own.read_file("x.csv", "id,title,kind\n1,a,target\n2,b,target\n3,c,target\n")
    assert len(rows) == 2 and cut
