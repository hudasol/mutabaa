"""Import contract for the Python layers (see docs/ARCHITECTURE.md, section 6).

A module may import modules in its own layer or in a lower layer, never in a higher one.
Every module in pipeline/ must be assigned to a layer, so a new module cannot skip the contract.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parent.parent / "pipeline"

LAYERS: dict[str, int] = {
    # 0. contracts and pure helpers: no imports from the package
    "schemas": 0, "stats": 0, "render": 0,
    # 1. reading the repository
    "io": 1,
    # 2. engines: deterministic rules over typed records
    "score": 2, "status": 2, "own": 2, "questions": 2, "sensitivity": 2, "synth": 2, "synth_b": 2,
    "validate": 2, "verify_live": 2, "diff": 2,
    # 3. analysis and reporting over engine output
    "robustness": 3, "own_report": 3, "calibration": 3, "agreement": 3, "facts": 3, "evaluate": 3,
    "evaluate_real": 3, "schema_export": 3,
    # 4. command line
    "__main__": 4, "__init__": 4,
}


def package_imports(path: Path) -> set[str]:
    """Names of pipeline modules imported by one file (relative or absolute imports)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level >= 1:
                if node.module:
                    out.add(node.module.split(".")[0])
                else:
                    out.update(a.name.split(".")[0] for a in node.names)
            elif node.module and node.module.split(".")[0] == "pipeline":
                parts = node.module.split(".")
                if len(parts) > 1:
                    out.add(parts[1])
                else:
                    out.update(a.name for a in node.names)
        elif isinstance(node, ast.Import):
            for a in node.names:
                parts = a.name.split(".")
                if parts[0] == "pipeline" and len(parts) > 1:
                    out.add(parts[1])
    return out


def violations(graph: dict[str, set[str]], layers: dict[str, int]) -> list[str]:
    bad = []
    for mod, deps in sorted(graph.items()):
        for dep in sorted(deps):
            if dep in layers and layers[dep] > layers[mod]:
                bad.append(f"{mod} (layer {layers[mod]}) imports {dep} (layer {layers[dep]})")
    return bad


def graph() -> dict[str, set[str]]:
    return {p.stem: package_imports(p) for p in sorted(PKG.glob("*.py"))}


def test_every_module_has_a_layer():
    missing = sorted(set(graph()) - set(LAYERS))
    assert missing == [], f"assign a layer in tests/test_layers.py and docs/ARCHITECTURE.md: {missing}"


def test_no_lower_layer_imports_a_higher_one():
    assert violations(graph(), LAYERS) == []


def test_layer_zero_imports_nothing_from_the_package():
    g = graph()
    assert {m: g[m] for m in g if LAYERS.get(m) == 0 and g[m]} == {}


@pytest.mark.parametrize(
    "g,expected",
    [
        ({"score": {"schemas"}}, 0),
        ({"schemas": {"score"}}, 1),
        ({"io": {"facts"}, "facts": {"io"}}, 1),
    ],
)
def test_contract_detects_upward_imports(g, expected):
    assert len(violations(g, LAYERS)) == expected


def test_parser_reads_relative_and_absolute_imports(tmp_path):
    f = tmp_path / "m.py"
    f.write_text(
        "from .schemas import X\nfrom . import io\nimport pipeline.score\nfrom pipeline import status\n"
    )
    assert package_imports(f) == {"schemas", "io", "score", "status"}


def test_architecture_document_lists_every_module():
    text = (PKG.parent / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
    missing = [m for m in graph() if m not in ("__init__",) and f"`{m}`" not in text]
    assert missing == [], f"docs/ARCHITECTURE.md does not list: {missing}"
