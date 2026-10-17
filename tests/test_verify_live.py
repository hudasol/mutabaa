"""The live verifier, exercised with a fake fetcher. No network is used."""

from __future__ import annotations

import pathlib
import urllib.error

import pytest

from pipeline import verify_live as vl
from pipeline.io import load_real


@pytest.fixture(scope="module")
def src():
    s = load_real().sources[0]
    return s.model_copy(
        update={"expect_present": ["AED 13 billion|AED13bn", "50%"], "expect_absent": ["70% faster"]}
    )


def page(body: str, status: int = 200):
    return lambda url: vl.Fetched(status, body)


def test_verified_when_figures_are_visible(src):
    r = vl.check_source(src, page("<p>AED&nbsp;13 billion and 50 per cent</p>"))
    assert r["result"] == "verified" and r["missing"] == []


def test_failed_when_a_figure_is_missing_or_an_absent_figure_appears(src):
    r = vl.check_source(src, page("<p>AED 13 billion. Up to 70% faster.</p>"))
    assert r["result"] == "failed"
    assert r["missing"] == ["50%"] and r["unexpected"] == ["70% faster"]


def test_figures_hidden_in_scripts_are_not_counted_as_visible(src):
    r = vl.check_source(src, page("<p>AED 13 billion</p><script>var x = '50%';</script>"))
    assert r["result"] == "verified" and r["in_markup_only"] == ["50%"]


def test_unreachable_on_http_error_or_empty_body(src):
    assert vl.check_source(src, lambda u: vl.Fetched(403, "", "HTTP 403"))["result"] == "unreachable"
    assert vl.check_source(src, page(""))["result"] == "unreachable"


def test_no_expectations(src):
    bare = src.model_copy(update={"expect_present": [], "expect_absent": []})
    assert vl.check_source(bare, page("<p>text</p>"))["result"] == "no-expectations"


def test_run_filters_and_summarises(src):
    other = src.model_copy(update={"id": "S98"})
    rep = vl.run([src, other], fetch=page("<p>AED 13 billion</p>"), only={"S98"})
    assert set(rep["results"]) == {"S98"}
    rep["results"]["S97"] = {"result": "unreachable", "error": "HTTP 403"}
    rep["results"]["S96"] = {"result": "verified", "in_markup_only": ["x"]}
    text = vl.summarise(rep)
    assert "S98  failed" in text and "(HTTP 403)" in text and "in page markup" in text
    assert vl.dumps(rep).endswith("\n")


def test_robots_disallow_is_reported_unreachable_and_the_page_is_not_fetched(src):
    asked = []

    def fetch(url):
        asked.append(url)
        if url.endswith("/robots.txt"):
            return vl.Fetched(200, "User-agent: *\nDisallow: /")
        return vl.Fetched(200, "<p>AED 13 billion 50%</p>")

    r = vl.check_source(src, fetch)
    assert r["result"] == "unreachable" and "robots" in r["error"]
    assert all(u.endswith("/robots.txt") for u in asked)


def test_robots_403_forbids_and_missing_robots_allows(src):
    def forbid(url):
        return vl.Fetched(403, "", "HTTP 403") if url.endswith("/robots.txt") else vl.Fetched(200, "<p>x</p>")

    def missing(url):
        if url.endswith("/robots.txt"):
            return vl.Fetched(404, "", "HTTP 404")
        return vl.Fetched(200, "<p>AED 13 billion 50%</p>")

    assert vl.check_source(src, forbid)["error"] == "disallowed by robots.txt"
    assert vl.check_source(src, missing)["result"] == "verified"


def test_robots_file_is_read_once_per_host_and_runs_pause(src, monkeypatch):
    asked, slept = [], []
    monkeypatch.setattr(vl.time, "sleep", lambda s: slept.append(s))

    def fetch(url):
        asked.append(url)
        return vl.Fetched(200, "<p>AED 13 billion 50%</p>")

    two = [src, src.model_copy(update={"id": "S98"})]
    vl.run(two, fetch=fetch)
    assert sum(u.endswith("/robots.txt") for u in asked) == 1
    assert slept == [1.0]


def test_norm_treats_dashes_and_per_cent_alike():
    assert vl.norm("Fifty per cent \u2014 2025\u20132027") == vl.norm("fifty% - 2025-2027")


class _Resp:
    status = 200

    def __init__(self, body: bytes):
        self._b = body
        self.headers = self

    def get_content_charset(self):
        return "utf-8"

    def read(self, n):
        return self._b[:n]

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_fetch_once_reads_body_and_maps_errors(monkeypatch):
    monkeypatch.setattr(vl.urllib.request, "urlopen", lambda req, timeout: _Resp(b"<p>ok</p>"))
    assert vl._fetch_once("https://example.org", 5) == vl.Fetched(200, "<p>ok</p>")

    def http_error(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, None)

    monkeypatch.setattr(vl.urllib.request, "urlopen", http_error)
    assert vl._fetch_once("https://example.org", 5).status == 403

    def url_error(req, timeout):
        raise urllib.error.URLError("certificate verify failed")

    monkeypatch.setattr(vl.urllib.request, "urlopen", url_error)
    f = vl._fetch_once("https://example.org", 5)
    assert f.status is None and "URLError" in f.error


def test_http_fetch_retries_only_when_there_is_no_status(monkeypatch):
    calls = []

    def flaky(url, timeout):
        calls.append(url)
        return vl.Fetched(None, "", "reset") if len(calls) < 2 else vl.Fetched(200, "body")

    monkeypatch.setattr(vl, "_fetch_once", flaky)
    monkeypatch.setattr(vl.time, "sleep", lambda s: None)
    assert vl.http_fetch("https://example.org").status == 200 and len(calls) == 2

    calls.clear()
    monkeypatch.setattr(
        vl, "_fetch_once", lambda url, timeout: calls.append(url) or vl.Fetched(403, "", "HTTP 403")
    )
    assert vl.http_fetch("https://example.org").status == 403 and len(calls) == 1


def test_requests_identify_the_tool_and_keep_tls_checks(monkeypatch):
    seen = {}

    def capture(req, timeout):
        seen["ua"] = req.get_header("User-agent")
        return _Resp(b"x")

    monkeypatch.setattr(vl.urllib.request, "urlopen", capture)
    vl._fetch_once("https://example.org", 5)
    assert seen["ua"].startswith("MutabaaVerifier/")
    src = pathlib.Path(vl.__file__).read_text(encoding="utf-8")
    unsafe_markers = ("CERT_NONE", "check_hostname = False", "_create_unverified", "verify_mode", "ssl.")
    for unsafe in unsafe_markers:
        assert unsafe not in src, unsafe
