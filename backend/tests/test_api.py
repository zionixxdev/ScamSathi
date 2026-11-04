"""API integration tests."""

from __future__ import annotations

from app.api import deps


def test_health(client) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["ai_provider"] == "none"


def test_security_headers_are_present(client) -> None:
    response = client.get("/api/v1/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["Cache-Control"] == "no-store"


def test_cors_allows_the_configured_origin(client) -> None:
    response = client.options(
        "/api/v1/analyze/message",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_rejects_unknown_origin(client) -> None:
    response = client.options(
        "/api/v1/analyze/message",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in response.headers


def test_analyze_stores_and_lists_history(client, headers) -> None:
    response = client.post(
        "/api/v1/analyze/message",
        headers=headers,
        json={"content": "Complete your KYC now at http://sbi-kyc-verify.top/update or account blocked"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["stored"] is True
    scan_id = body["scan_id"]

    listing = client.get("/api/v1/history", headers=headers)
    assert listing.status_code == 200
    page = listing.json()
    assert page["total"] == 1
    assert page["items"][0]["scan_id"] == scan_id

    single = client.get(f"/api/v1/history/{scan_id}", headers=headers)
    assert single.status_code == 200
    assert single.json()["risk_score"] == body["risk_score"]


def test_history_is_isolated_between_clients(client, headers) -> None:
    client.post(
        "/api/v1/analyze/message",
        headers=headers,
        json={"content": "You won a lottery, pay the processing fee to claim"},
    )
    other = {"X-Client-Id": "someoneelse12345"}
    assert client.get("/api/v1/history", headers=other).json()["total"] == 0


def test_delete_removes_the_record(client, headers) -> None:
    created = client.post(
        "/api/v1/analyze/message", headers=headers, json={"content": "Share your OTP with us to verify"}
    ).json()
    scan_id = created["scan_id"]
    assert client.delete(f"/api/v1/history/{scan_id}", headers=headers).status_code == 204
    assert client.get(f"/api/v1/history/{scan_id}", headers=headers).status_code == 404
    assert client.delete(f"/api/v1/history/{scan_id}", headers=headers).status_code == 404


def test_scan_without_client_id_is_not_stored(client) -> None:
    response = client.post("/api/v1/analyze/message", json={"content": "Share your OTP now"})
    assert response.status_code == 200
    assert response.json()["stored"] is False
    assert client.get("/api/v1/history").json()["total"] == 0


def test_store_can_be_opted_out(client, headers) -> None:
    response = client.post(
        "/api/v1/analyze/message",
        headers=headers,
        json={"content": "Share your OTP now", "store": False},
    )
    assert response.json()["stored"] is False


def test_stats_reflect_only_this_client(client, headers) -> None:
    client.post(
        "/api/v1/analyze/message",
        headers=headers,
        json={"content": "Dear Customer, your account will be blocked. Complete KYC at http://sbi-kyc.top"},
    )
    stats = client.get("/api/v1/stats", headers=headers).json()
    assert stats["total_scans"] >= 1
    assert stats["demo_data"] is False
    assert stats["by_category"]


def test_stats_without_client_id_returns_empty(client) -> None:
    stats = client.get("/api/v1/stats").json()
    assert stats["total_scans"] == 0
    assert "no client id" in stats["note"].lower()


def test_url_analysis_endpoint(client, headers) -> None:
    response = client.post("/api/v1/analyze/url", headers=headers, json={"url": "http://sbi-kyc-verify.top/login"})
    assert response.status_code == 200
    body = response.json()
    assert body["scan_type"] == "url"
    assert body["risk_score"] >= 50
    assert body["url_analysis"]["host"] == "sbi-kyc-verify.top"


def test_invalid_scheme_returns_a_safe_error(client) -> None:
    response = client.post("/api/v1/analyze/url", json={"url": "javascript:alert(1)"})
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "invalid_scheme"
    assert "Traceback" not in response.text


def test_oversized_message_is_rejected(client) -> None:
    response = client.post("/api/v1/analyze/message", json={"content": "a" * 6000})
    assert response.status_code == 422


def test_unknown_risk_filter_is_rejected(client, headers) -> None:
    response = client.get("/api/v1/history", headers=headers, params={"risk_level": "Nope"})
    assert response.status_code == 404


def test_missing_scan_returns_404(client, headers) -> None:
    assert client.get("/api/v1/history/does-not-exist", headers=headers).status_code == 404


def test_invalid_client_id_is_ignored(client) -> None:
    response = client.post(
        "/api/v1/analyze/message",
        headers={"X-Client-Id": "bad id with spaces"},
        json={"content": "Share your OTP now"},
    )
    assert response.status_code == 200
    assert response.json()["stored"] is False


def test_html_in_content_is_treated_as_data(client) -> None:
    payload = "<script>alert('xss')</script> Your KYC is pending"
    response = client.post("/api/v1/analyze/message", json={"content": payload})
    assert response.status_code == 200
    assert "<script>" in response.json()["excerpt"]


def test_rate_limit_returns_429(client, headers) -> None:
    original = deps.analyze_limiter.max_requests
    deps.analyze_limiter.max_requests = 2
    deps.reset_rate_limiters()
    try:
        for _ in range(2):
            assert client.post("/api/v1/analyze/message", json={"content": "hello"}).status_code == 200
        blocked = client.post("/api/v1/analyze/message", json={"content": "hello"})
        assert blocked.status_code == 429
        assert blocked.json()["error"]["code"] == "rate_limited"
    finally:
        deps.analyze_limiter.max_requests = original
        deps.reset_rate_limiters()
