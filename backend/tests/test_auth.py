from fastapi.testclient import TestClient
from backend.app.main import app
import backend.app.main as server


def test_api_key_protects_nonpublic_endpoints(monkeypatch):
    monkeypatch.setattr(server, 'API_KEY', 'secret-example-for-tests')
    with TestClient(app) as client:
        assert client.get('/health').status_code == 200
        denied = client.get('/history')
        assert denied.status_code == 401
        assert denied.headers.get('X-Request-ID')
        accepted = client.get('/history', headers={'X-API-Key': 'secret-example-for-tests'})
        assert accepted.status_code == 200
