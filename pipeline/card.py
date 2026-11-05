"""Definition Card: read, validate and apply one declared definition of a headline percentage.

A card states the unit, scope, maturity threshold and guardrails behind a headline percentage. Applying it
runs the existing Definition Lab calculation (sensitivity.share) on a registry. The calculation is not
changed here. Cards in data/examples/ are synthetic and say so.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from .schemas import DefinitionCard, Registry
from .sensitivity import share


def validate(text: str) -> tuple[DefinitionCard | None, list[str]]:
    """Parse a card. Returns the card and no errors, or None and one readable line per problem."""
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, [f"not valid JSON: {exc.msg} (line {exc.lineno})"]
    if not isinstance(raw, dict):
        return None, ["a card is one JSON object"]
    try:
        return DefinitionCard.model_validate(raw), []
    except ValidationError as exc:
        return None, [f"{'.'.join(str(p) for p in e['loc']) or 'card'}: {e['msg']}" for e in exc.errors()]


def apply(card: DefinitionCard, registry: Registry) -> dict[str, Any]:
    """The headline percentage under the declared definition, on the given registry."""
    s = share(registry, card.definition)
    return {
        "share": None if s is None else round(s, 6),
        "definition": card.definition.model_dump(),
        "registry_is_synthetic": True,
    }
