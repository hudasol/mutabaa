"""The drift comparison, run on a recorded fixture with no network."""

from __future__ import annotations

from pipeline.io import load_real
from pipeline.monitor import compare, needs_attention, render
from pipeline.verify_live import Fetched, run

PAGES = {
    "S01": "<p>Reach 50% in two years</p>",
    "S02": "<p>Reach 50% in two years</p>",
}


def _sources():
    s = [x for x in load_real().sources if x.id in ("S01", "S02")]
    return [x.model_copy(update={"expect_present": ["50%"], "expect_absent": []}) for x in s]


def _fetch_for(pages):
    def f(url: str) -> Fetched:
        if url.endswith("/robots.txt"):
            return Fetched(404, "", "HTTP 404")
        for src in _sources():
            if src.url == url:
                body = pages.get(src.id)
                return Fetched(200, body) if body is not None else Fetched(None, "", "URLError: down")
        return Fetched(404, "", "HTTP 404")
    return f


def _report(pages):
    return run(_sources(), fetch=_fetch_for(pages), pause=0)


def test_no_change_means_no_issue():
    base = _report(PAGES)
    cmp = compare(base, _report(PAGES))
    assert cmp["counts"]["unchanged"] == 2 and not needs_attention(cmp)


def test_changed_text_is_reported_by_hash():
    base = _report(PAGES)
    cmp = compare(base, _report({**PAGES, "S02": "<p>Reach 50% in two years, extended to 2030</p>"}))
    assert [r["id"] for r in cmp["changed"]] == ["S02"] and cmp["changed"][0]["reason"] == "visible text hash"
    assert needs_attention(cmp)


def test_new_outage_raises_attention_but_an_old_one_does_not():
    base = _report(PAGES)
    down = compare(base, _report({"S01": PAGES["S01"]}))
    assert [r["id"] for r in down["newly_unreachable"]] == ["S02"] and needs_attention(down)
    again = compare(_report({"S01": PAGES["S01"]}), _report({"S01": PAGES["S01"]}))
    assert again["counts"]["still_unreachable"] == 1 and not needs_attention(again)


def test_report_says_no_ledger_record_changed():
    text = render("2026-01-05", compare(_report(PAGES), _report(PAGES)))
    assert "No ledger record was changed" in text and text.startswith("# Source drift report, 2026-01-05")
