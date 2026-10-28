"""Prevent shipping a synthetic fraud model as an actual production service."""
import pytest
from backend.app.core import config


def secure_synthetic_staging(monkeypatch):
    monkeypatch.setattr(config, "ENVIRONMENT", "staging")
    monkeypatch.setattr(config, "API_KEY", "0123456789abcdef0123456789abcdef")
    monkeypatch.setattr(config, "CORS_ORIGINS", ["https://restricted.example.org"])
    monkeypatch.setattr(config, "DATABASE_URL", "postgresql+psycopg://user:pass@host/staging")
    monkeypatch.setattr(config, "DEMO_RATE_LIMIT", 60)
    monkeypatch.setattr(config, "MAX_REQUEST_BYTES", 16384)


def test_restricted_staging_accepts_a_synthetic_demo(monkeypatch):
    secure_synthetic_staging(monkeypatch)
    config.validate_configuration()


def test_production_always_refuses_this_synthetic_model(monkeypatch):
    secure_synthetic_staging(monkeypatch)
    monkeypatch.setattr(config, "ENVIRONMENT", "production")
    with pytest.raises(RuntimeError, match="prohibited in production"):
        config.validate_configuration()


def test_staging_refuses_missing_secret_or_unsafe_cors(monkeypatch):
    secure_synthetic_staging(monkeypatch)
    monkeypatch.setattr(config, "API_KEY", "short")
    with pytest.raises(RuntimeError, match="API_KEY"):
        config.validate_configuration()
    monkeypatch.setattr(config, "API_KEY", "a" * 40)
    monkeypatch.setattr(config, "CORS_ORIGINS", ["http://untrusted.example.org"])
    with pytest.raises(RuntimeError, match="HTTPS"):
        config.validate_configuration()


def test_staging_requires_gateway_style_boundaries(monkeypatch):
    secure_synthetic_staging(monkeypatch)
    monkeypatch.setattr(config, "DATABASE_URL", "sqlite:///unsafe.sqlite")
    with pytest.raises(RuntimeError, match="PostgreSQL"):
        config.validate_configuration()
    monkeypatch.setattr(config, "DATABASE_URL", "postgresql+psycopg://user:pass@host/staging")
    monkeypatch.setattr(config, "DEMO_RATE_LIMIT", 0)
    with pytest.raises(RuntimeError, match="rate limit"):
        config.validate_configuration()


def test_request_byte_limit_cannot_be_disabled(monkeypatch):
    secure_synthetic_staging(monkeypatch)
    monkeypatch.setattr(config, "MAX_REQUEST_BYTES", 0)
    with pytest.raises(RuntimeError, match="MAX_REQUEST_BYTES"):
        config.validate_configuration()
