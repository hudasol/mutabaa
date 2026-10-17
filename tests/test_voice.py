"""Public voice rules for prose in the repository.

The rules live in tests/voice_rules.json so they can be read and changed in one place.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RULES = json.loads((Path(__file__).parent / "voice_rules.json").read_text(encoding="utf-8"))

EM_DASH = chr(0x2014)
# Pictographic ranges. Arrows, maths signs and box drawing characters are not emoji and are not matched.
_EMOJI = re.compile(r"[\U0001f000-\U0001faff\u2600-\u26ff\u2700-\u27bf\u2b50\u2b55\u2300-\u23ff]")


_URL = re.compile(r"(https?://|`?[a-z0-9.-]+\.(?:ae|com|org)/)\S*")


def prose_files() -> list[Path]:
    seen: dict[str, Path] = {}
    for g in RULES["prose_globs"]:
        for p in sorted(ROOT.glob(g)):
            if p.is_file():
                seen[p.relative_to(ROOT).as_posix()] = p
    return [seen[k] for k in sorted(seen)]


def violations(rel: str, text: str) -> list[str]:
    """Return a list of 'file:line: problem' strings for one prose file."""
    out: list[str] = []
    allowed = set(RULES["allowed_emoji"])
    vendors = re.compile(r"\b(" + "|".join(map(re.escape, RULES["vendor_words"])) + r")\b")
    unis = re.compile("|".join(RULES["university_patterns"]), re.IGNORECASE)
    orgs = re.compile(r"\b(" + "|".join(map(re.escape, RULES["org_names"])) + r")\b")
    check_orgs = rel not in RULES["org_names_allowed_in"]
    for n, raw in enumerate(text.splitlines(), 1):
        where = f"{rel}:{n}"
        line = _URL.sub(" ", raw)  # links are identifiers, not prose
        if EM_DASH in line:
            out.append(f"{where}: em dash")
        for ch in _EMOJI.findall(line):
            if ch not in allowed:
                out.append(f"{where}: emoji {ch!r}")
        if m := vendors.search(line):
            out.append(f"{where}: assistant or vendor name {m.group(0)!r}")
        if m := unis.search(line):
            out.append(f"{where}: university {m.group(0)!r}")
        if check_orgs and (m := orgs.search(line)):
            out.append(f"{where}: real organisation name {m.group(0)!r} outside docs/CONTEXT.md")
    return out


def test_prose_files_found():
    rels = {p.relative_to(ROOT).as_posix() for p in prose_files()}
    assert {"README.md", "CHANGELOG.md", "docs/CONTEXT.md"} <= rels


@pytest.mark.parametrize("path", prose_files(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_prose_follows_voice_rules(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    problems = violations(rel, path.read_text(encoding="utf-8"))
    assert problems == [], "\n".join(problems)


def test_no_em_dash_in_any_tracked_text_file():
    try:
        files = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git is not available")
    bad = []
    for rel in files:
        if rel in RULES["em_dash_exempt_files"]:
            continue
        p = ROOT / rel
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        if EM_DASH in text:
            bad.append(rel)
    assert bad == [], f"em dash in: {bad}"


@pytest.mark.parametrize(
    "line,expected",
    [
        ("A plain sentence.", []),
        ("A pause \u2014 here.", ["em dash"]),
        ("Rated by Claude.", ["assistant or vendor name"]),
        ("Built at a university.", ["university"]),
        ("The DGE said so.", ["real organisation name"]),
        ("A tulip \U0001f337 is fine.", []),
        ("A rocket \U0001f680 is not.", ["emoji"]),
        ("Arrows \u2192 and \u2265 signs are fine.", []),
    ],
)
def test_rules_catch_known_violations(line, expected):
    found = violations("docs/EXAMPLE.md", line)
    assert len(found) == len(expected)
    for f, e in zip(found, expected, strict=True):
        assert e in f


def test_context_document_may_name_entities():
    assert violations("docs/CONTEXT.md", "The DGE published a statement.") == []


def test_context_cites_every_source():
    sources = json.loads((ROOT / "data" / "real" / "sources.json").read_text(encoding="utf-8"))
    text = (ROOT / "docs" / "CONTEXT.md").read_text(encoding="utf-8")
    for s in sources:
        assert f"| {s['id']} |" in text and s["url"] in text, s["id"]
