import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core import config


def test_response_security_headers():
    with TestClient(app) as client:
        response = client.get('/health')
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert response.headers['Cache-Control'] == 'no-store'
        assert response.headers['X-Request-ID']


def test_oversized_payload_is_rejected():
    with TestClient(app) as client:
        result = client.post('/predict', data='x' * 20000,
                             headers={'Content-Type': 'application/json'})
        assert result.status_code == 413


def test_prod_rejects_missing_auth_and_sqlite(monkeypatch):
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    monkeypatch.setattr(config, 'API_KEY', '')
    with pytest.raises(RuntimeError, match='API_KEY'):
        config.validate_configuration()
    monkeypatch.setattr(config, 'API_KEY', 's' * 40)
    with pytest.raises(RuntimeError, match='HTTPS'):
        config.validate_configuration()
    monkeypatch.setattr(config, 'CORS_ORIGINS', ['https://risk.example.org'])
    with pytest.raises(RuntimeError, match='PostgreSQL'):
        config.validate_configuration()


def test_oversized_chunked_payload_is_rejected():
    # Streaming iterator causes httpx to omit Content-Length.
    with TestClient(app) as client:
        response = client.post('/predict', content=iter([b'{', b'x' * 20000]),
                               headers={'Content-Type': 'application/json'})
        assert response.status_code == 413
        assert response.headers.get('x-request-id')
