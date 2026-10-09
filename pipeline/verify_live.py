"""Check each source's raw page against what the extraction notes claim.

Why this exists: the extraction notes were written from summaries, not page text, so the usual
anchor check only proves the notes agree with themselves. This tool fetches the page and checks
that the figures the notes rely on are really there, and that figures the notes say are absent
really are absent. It needs a machine with network access. It uses the standard library only.

What it does not do: it does not store page text, and it does not understand meaning. A figure
present on the page proves the number exists there, not that the notes read it correctly.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser

from .schemas import Source

USER_AGENT = "MutabaaVerifier/1.0 (+https://github.com/hudasol/mutabaa; checks published figures)"
TOOL_VERSION = "1"
MAX_BYTES = 8_000_000


class _Text(HTMLParser):
    _SKIP = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._depth += 1

    def handle_endtag(self, tag):
        if tag in self._SKIP and self._depth:
            self._depth -= 1

    def handle_data(self, data):
        if not self._depth:
            self.parts.append(data)


def visible_text(markup: str) -> str:
    p = _Text()
    p.feed(markup)
    return " ".join(p.parts)


_DASH = str.maketrans({"‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "’": "'", "‘": "'", " ": " "})


def norm(s: str) -> str:
    """Lowercase, unescape, and drop spaces and commas so 'AED 13 billion' matches 'AED13 billion'."""
    s = html.unescape(s).translate(_DASH).lower()
    s = re.sub(r"per\s*cent", "%", s)  # "95 per cent", "95 percent" and "95%" are the same figure
    return re.sub(r"[\s,]+", "", s)


def contains(haystack_norm: str, expectation: str) -> bool:
    return any(norm(alt) in haystack_norm for alt in expectation.split("|") if alt.strip())


@dataclass
class Fetched:
    status: int | None
    body: str
    error: str | None = None


Fetcher = Callable[[str], Fetched]


def http_fetch(url: str, timeout: int = 30, attempts: int = 4) -> Fetched:
    """Fetch with a few retries: some government hosts reset connections intermittently."""
    last = Fetched(None, "", "no attempt")
    for i in range(attempts):
        last = _fetch_once(url, timeout)
        if last.status is not None or i == attempts - 1:
            return last
        time.sleep(1.5 * (i + 1))
    return last


def _fetch_once(url: str, timeout: int) -> Fetched:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (https only, validated)
            raw = r.read(MAX_BYTES)
            charset = r.headers.get_content_charset() or "utf-8"
            return Fetched(r.status, raw.decode(charset, errors="replace"))
    except urllib.error.HTTPError as e:
        return Fetched(e.code, "", f"HTTP {e.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return Fetched(None, "", f"{type(e).__name__}: {e}")


def check_source(src: Source, fetch: Fetcher = http_fetch) -> dict:
    f = fetch(src.url)
    base = {
        "checked_at": datetime.now(UTC).strftime("%Y-%m-%d"),
        "url": src.url,
        "http_status": f.status,
        "checked_present": len(src.expect_present),
        "checked_absent": len(src.expect_absent),
    }
    if f.error or f.status != 200 or not f.body:
        return {
            **base,
            "result": "unreachable",
            "error": f.error or "empty response",
            "missing": [],
            "unexpected": [],
        }
    text_n = norm(visible_text(f.body))
    markup_n = norm(f.body)
    missing, in_markup_only = [], []
    for e in src.expect_present:
        if contains(text_n, e):
            continue
        (in_markup_only if contains(markup_n, e) else missing).append(e)
    unexpected = [e for e in src.expect_absent if contains(markup_n, e)]
    if missing or unexpected:
        result = "failed"
    elif not src.expect_present and not src.expect_absent:
        result = "no-expectations"
    else:
        result = "verified"
    return {
        **base,
        "result": result,
        "missing": missing,
        "in_markup_only": in_markup_only,
        "unexpected": unexpected,
        "visible_text_chars": len(text_n),
        "visible_text_sha256": hashlib.sha256(text_n.encode()).hexdigest(),
    }


def run(sources: list[Source], fetch: Fetcher = http_fetch, only: set[str] | None = None) -> dict:
    results = {s.id: check_source(s, fetch) for s in sources if not only or s.id in only}
    return {
        "run_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tool_version": TOOL_VERSION,
        "user_agent": USER_AGENT,
        "results": results,
    }


def summarise(report: dict) -> str:
    lines = []
    for sid, r in sorted(report["results"].items()):
        extra = ""
        if r["result"] == "failed":
            extra = f" missing={r['missing']} unexpected={r['unexpected']}"
        elif r["result"] == "unreachable":
            extra = f" ({r['error']})"
        elif r.get("in_markup_only"):
            extra = f" (in page markup but not visible text: {r['in_markup_only']})"
        lines.append(f"{sid}  {r['result']:<15}{extra}")
    return "\n".join(lines)


def dumps(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
