"""Render a Markdown template whose {fact.key} placeholders become marked, checked numbers.

A placeholder {robustness.flip_rate} is replaced by <!-- fact:robustness.flip_rate -->80%<!-- /fact -->,
so tests/test_docs_agree.py can later check the document against results/facts.json.
"""

from __future__ import annotations

import re

_PLACEHOLDER = re.compile(r"\{([a-z][\w]*(?:\.[\w\-]+)+)\}")


def render(template: str, facts: dict[str, dict]) -> str:
    def sub(m: re.Match) -> str:
        key = m.group(1)
        if key not in facts:
            raise KeyError(f"template cites unknown fact {key!r}")
        return f"<!-- fact:{key} -->{facts[key]['text']}<!-- /fact -->"

    return _PLACEHOLDER.sub(sub, template)


_MARKED = re.compile(r"(<!-- fact:([\w.\-]+) -->)(.*?)(<!-- /fact -->)")


def refresh(text: str, facts: dict[str, dict]) -> str:
    """Rewrite the value inside every marked number so that it matches the facts."""

    def sub(m: re.Match) -> str:
        key = m.group(2)
        if key not in facts:
            raise KeyError(f"document cites unknown fact {key!r}")
        return f"{m.group(1)}{facts[key]['text']}{m.group(4)}"

    return _MARKED.sub(sub, text)
