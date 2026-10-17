"""JSON Schema files generated from the pydantic models, so other tools can validate records.

`python -m pipeline schema` writes schema/<name>.schema.json. tests/test_schema.py fails when a file is stale.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from .schemas import (
    Claim,
    Commitment,
    Definition,
    Evidence,
    Registry,
    SearchEntry,
    ServiceItem,
    Source,
    StatusResult,
    VerifiabilityResult,
)

MODELS: dict[str, type[BaseModel]] = {
    "commitment": Commitment,
    "source": Source,
    "evidence": Evidence,
    "claim": Claim,
    "search_entry": SearchEntry,
    "verifiability_result": VerifiabilityResult,
    "status_result": StatusResult,
    "service_item": ServiceItem,
    "registry": Registry,
    "definition": Definition,
}


def schema_text(model: type[BaseModel]) -> str:
    return json.dumps(model.model_json_schema(), indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def generate() -> dict[str, str]:
    return {f"{name}.schema.json": schema_text(m) for name, m in MODELS.items()}


def write(out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, text in generate().items():
        p = out / name
        p.write_text(text, encoding="utf-8", newline="\n")
        paths.append(p)
    return paths
