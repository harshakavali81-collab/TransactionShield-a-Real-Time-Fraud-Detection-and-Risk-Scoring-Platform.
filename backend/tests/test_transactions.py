from fastapi.testclient import TestClient
from backend.app.main import app

def test_history_stats_analytics():
    with TestClient(app) as client:
        history=client.get('/history?limit=5')
        assert history.status_code==200 and isinstance(history.json(),list)
        stats=client.get('/statistics')
        assert stats.status_code==200
        assert 'total_transactions' in stats.json()
        analytics=client.get('/analytics')
        assert analytics.status_code==200
        assert 'distribution' in analytics.json()

def test_404_and_limit_rejected():
    with TestClient(app) as client:
        assert client.get('/transactions/not-a-real-id').status_code==404
        assert client.get('/history?limit=999999').status_code==422
