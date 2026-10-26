from fastapi.testclient import TestClient
from backend.app.main import app

def test_health():
    with TestClient(app) as client:
        res=client.get('/health')
    assert res.status_code==200
    assert res.json()['status']=='ok'

def test_metrics():
    with TestClient(app) as client: response=client.get('/metrics')
    assert response.status_code==200
