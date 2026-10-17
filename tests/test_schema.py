"""Generated JSON Schema files are current, and the TypeScript types use the same field names."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from pipeline import schema_export

ROOT = Path(__file__).resolve().parent.parent
TYPES = ROOT / "site" / "src" / "types.ts"

# TypeScript type name -> generated schema file, for models the site and the pipeline share.
SHARED = {
    "Anchor": ("commitment.schema.json", "Anchor"),
    "Commitment": ("commitment.schema.json", None),
    "Source": ("source.schema.json", None),
    "Evidence": ("evidence.schema.json", None),
    "Claim": ("claim.schema.json", None),
    "SearchEntry": ("search_entry.schema.json", None),
    "Score": ("verifiability_result.schema.json", None),
    "Status": ("status_result.schema.json", None),
    "Item": ("service_item.schema.json", None),
    "Definition": ("definition.schema.json", None),
}


def ts_fields(source: str, name: str) -> set[str]:
    """Top level field names of `export type Name = { ... }` in a TypeScript file."""
    m = re.search(rf"export type {name} = \{{", source)
    assert m, f"type {name} not found in types.ts"
    depth, i, start = 1, m.end(), m.end()
    while depth:
        depth += {"{": 1, "}": -1}.get(source[i], 0)
        i += 1
    body = source[start : i - 1]
    fields, depth, token = set(), 0, ""
    for ch in body:
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        if depth == 0:
            token += ch
            if ch in ";\n":
                token = ""
            mm = re.match(r"\s*([A-Za-z_]\w*)\??:\s*$", token)
            if mm:
                fields.add(mm.group(1))
                token = ""
        else:
            token = ""
    return fields


def schema_fields(file: str, defn: str | None) -> set[str]:
    s = json.loads((ROOT / "schema" / file).read_text(encoding="utf-8"))
    if defn:
        s = s["$defs"][defn]
    return set(s["properties"])


def test_schema_files_are_up_to_date():
    for name, text in schema_export.generate().items():
        p = ROOT / "schema" / name
        assert p.exists(), f"missing {p}; run `python -m pipeline schema`"
        assert p.read_text(encoding="utf-8") == text, f"{name} is stale; run `python -m pipeline schema`"


def test_no_orphan_schema_files():
    expected = set(schema_export.generate())
    assert {p.name for p in (ROOT / "schema").glob("*.json")} == expected


@pytest.mark.parametrize("ts_name", sorted(SHARED))
def test_typescript_types_match_schema_fields(ts_name):
    file, defn = SHARED[ts_name]
    assert ts_fields(TYPES.read_text(encoding="utf-8"), ts_name) == schema_fields(file, defn)


def test_ts_field_parser():
    src = "export type X = { a: string; b?: { c: number }; d: Record<string, boolean | null>;\n e: 1 | 2 };"
    assert ts_fields(src, "X") == {"a", "b", "d", "e"}


def test_synthetic_records_are_marked_in_the_schema():
    s = json.loads((ROOT / "schema" / "service_item.schema.json").read_text(encoding="utf-8"))
    assert s["properties"]["is_synthetic"]["const"] is True
