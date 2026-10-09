"""Load the repository data into typed models."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import TypeAdapter

from .schemas import Claim, Commitment, Evidence, SearchEntry, Source

ROOT = Path(__file__).resolve().parent.parent
REAL = ROOT / "data" / "real"


@dataclass
class RealData:
    sources: list[Source]
    commitments: list[Commitment]
    evidence: list[Evidence]
    claims: list[Claim]
    searches: list[SearchEntry]
    verification: dict


def _load(name: str, model: type):
    raw = json.loads((REAL / name).read_text(encoding="utf-8"))
    return TypeAdapter(list[model]).validate_python(raw)


def load_real() -> RealData:
    return RealData(
        sources=_load("sources.json", Source),
        commitments=_load("commitments.json", Commitment),
        evidence=_load("evidence.json", Evidence),
        claims=_load("claims.json", Claim),
        searches=TypeAdapter(list[SearchEntry]).validate_python(
            json.loads((REAL / "searchlog.json").read_text(encoding="utf-8"))["entries"]
        ),
        verification=json.loads((REAL / "verification.json").read_text(encoding="utf-8")),
    )
