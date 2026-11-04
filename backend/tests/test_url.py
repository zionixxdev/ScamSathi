"""URL analyser tests. No test performs network access."""

from __future__ import annotations

import pytest

from app.core.errors import AppError
from app.services.detection.engine import DetectionEngine
from app.services.url.analyzer import analyze_url


def test_official_bank_domain_is_low_risk() -> None:
    report = analyze_url("https://www.sbi.co.in/")
    assert report.risk_score == 0
    assert report.risk_level == "Low"
    assert report.findings == []
    assert report.mitigators


def test_typosquat_with_bait_path_is_high_risk() -> None:
    report = analyze_url("http://sbi-kyc-verify.top/update")
    assert report.risk_score >= 50
    assert report.lookalike_of == "sbi"
    assert {f.id for f in report.findings} >= {"suspicious_tld", "bait_keywords", "no_https"}


def test_brand_hidden_in_subdomain() -> None:
    report = analyze_url("https://sbi.co.in.secure-login.xyz/kyc")
    assert report.risk_score >= 50
    assert any(f.id in {"brand_in_subdomain", "lookalike_domain"} for f in report.findings)


def test_shortener_is_flagged() -> None:
    report = analyze_url("https://bit.ly/3xYz")
    assert report.is_shortener is True
    assert report.risk_score >= 25


def test_https_alone_is_not_proof_of_safety() -> None:
    report = analyze_url("https://hdfcbank-kyc.com/verify")
    assert report.https is True
    assert report.risk_score >= 25
    assert any(f.id == "lookalike_domain" for f in report.findings)


def test_plain_http_loses_the_https_mitigation() -> None:
    report = analyze_url("http://example.com/")
    assert report.https is False
    assert any(f.id == "no_https" for f in report.findings)


def test_private_ip_is_flagged_and_never_contacted() -> None:
    report = analyze_url("http://192.168.0.12/login")
    assert report.is_ip_literal is True
    assert any(f.id in {"internal_address", "ip_literal_host"} for f in report.findings)


def test_userinfo_trick_is_flagged() -> None:
    report = analyze_url("http://user@sbi.co.in@evil.example/")
    assert any(f.id == "userinfo_trick" for f in report.findings)


def test_punycode_is_flagged() -> None:
    report = analyze_url("https://xn--pypal-4ve.com/login")
    assert report.is_punycode is True
    assert any(f.id == "punycode_host" for f in report.findings)


@pytest.mark.parametrize(
    "url",
    ["javascript:alert(1)", "ftp://example.com/file", "file:///etc/passwd", "data:text/html,<h1>x</h1>"],
)
def test_non_http_schemes_are_rejected(url: str) -> None:
    with pytest.raises(AppError):
        analyze_url(url)


@pytest.mark.parametrize("url", ["", "   ", "not a url", "http://"])
def test_malformed_urls_are_rejected(url: str) -> None:
    with pytest.raises(AppError):
        analyze_url(url)


def test_query_string_and_fragment_are_stripped() -> None:
    report = analyze_url("https://example.com/path?token=SECRET#frag")
    assert "token" not in report.normalized
    assert report.normalized == "https://example.com/path"


def test_url_scan_never_touches_the_network(monkeypatch) -> None:
    import httpx

    class Boom:
        def __init__(self, *args, **kwargs):
            raise AssertionError("the URL scanner must not make network calls")

    monkeypatch.setattr(httpx, "AsyncClient", Boom)
    engine = DetectionEngine()
    import asyncio

    result = asyncio.run(engine.analyze_url_scan(url="http://sbi-kyc-verify.top/login"))
    assert result.scan_type == "url"
    assert result.risk_score >= 25
    assert result.url_analysis is not None
    assert result.url_analysis.reputation.checked is False


def test_reputation_is_reported_as_not_checked_without_a_key() -> None:
    import asyncio

    result = asyncio.run(DetectionEngine().analyze_url_scan(url="https://example.com/"))
    reputation = result.url_analysis.reputation
    assert reputation.checked is False
    assert "not checked" in reputation.note.lower()
