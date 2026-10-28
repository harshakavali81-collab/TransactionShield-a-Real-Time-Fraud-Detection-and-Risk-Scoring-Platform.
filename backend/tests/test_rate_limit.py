"""Single-process demonstration token bucket: functional and API regression tests."""
from fastapi.testclient import TestClient

import backend.app.main as server
from backend.app.core.rate_limit import TokenBucketLimiter
from backend.app.core import config


def test_token_bucket_enforces_limit_and_refills():
    limiter = TokenBucketLimiter(window_seconds=60)
    assert limiter.consume("alpha", 2, now=100) == 0
    assert limiter.consume("alpha", 2, now=100) == 0
    assert limiter.consume("alpha", 2, now=100) == 30
    assert limiter.consume("alpha", 2, now=130) == 0
    assert limiter.consume("alpha", 2, now=130) == 30
    assert limiter.consume("alpha", 2, now=160) == 0


def test_clients_independent_and_forwarded_header_not_trusted(monkeypatch):
    limiter = TokenBucketLimiter()
    assert limiter.consume("peer1", 1, now=0) == 0
    assert limiter.consume("peer1", 1, now=0) == 60
    assert limiter.consume("peer2", 1, now=0) == 0
    assert limiter.consume("peer2", 1, now=0) == 60


def test_bounded_memory_and_disabled_mode():
    limiter = TokenBucketLimiter(max_clients=2)
    assert limiter.consume("a", 1, now=0) == 0
    assert limiter.consume("b", 1, now=0) == 0
    assert limiter.consume("c", 1, now=0) == 0
    assert len(limiter._clients) == 2
    assert "a" not in limiter._clients
    assert limiter.consume("a", 0, now=0) == 0


def test_api_returns_429_and_retry_after(monkeypatch):
    monkeypatch.setattr(server, "API_KEY", "")
    monkeypatch.setattr(server, "DEMO_RATE_LIMIT", 2)
    monkeypatch.setattr(server, "rate_limiter", TokenBucketLimiter())
    with TestClient(server.app) as client:
        assert client.get("/history").status_code == 200
        assert client.get("/history").status_code == 200
        blocked = client.get("/history", headers={"X-Forwarded-For": "1.2.3.4"})
        assert blocked.status_code == 429
        assert int(blocked.headers["Retry-After"]) >= 1
        assert blocked.headers["X-Request-ID"]
        assert blocked.headers["Cache-Control"] == "no-store"
        assert client.get("/health").status_code == 200


def test_auth_and_cors_preflight(monkeypatch):
    monkeypatch.setattr(server, "API_KEY", "test-only-key")
    monkeypatch.setattr(server, "DEMO_RATE_LIMIT", 1)
    monkeypatch.setattr(server, "rate_limiter", TokenBucketLimiter())
    with TestClient(server.app) as client:
        preflight = client.options("/predict", headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-API-Key, Content-Type",
        })
        assert preflight.status_code == 200
        assert client.get("/history").status_code == 401
        blocked = client.get("/history", headers={"X-API-Key": "test-only-key"})
        assert blocked.status_code == 429


def test_config_rejects_unsafe_demo_limit(monkeypatch):
    monkeypatch.setattr(config, "DEMO_RATE_LIMIT", -1)
    try:
        config.validate_configuration()
        assert False, "negative limits must be rejected"
    except RuntimeError as exc:
        assert "DEMO_RATE_LIMIT" in str(exc)
