"""Local release self-check; not a substitute for pen-testing or production certification."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import ROOT, MODEL_PATH, METRICS_PATH
from ml.training.model_integrity import verify_model_artifacts


def main():
    verify_model_artifacts(MODEL_PATH, metrics_path=METRICS_PATH)
    assert (ROOT / 'migrations/versions/0001_initial_schema.py').exists()
    assert (ROOT / 'frontend/package.json').exists()
    with TestClient(app) as client:
        assert client.get('/health').status_code == 200
        assert client.get('/ready').status_code == 200
        assert client.get('/monitoring/overview').status_code == 200
        assert client.get('/metrics').status_code == 200
    print(json.dumps({'checks': 'passed', 'model': 'synthetic demo',
                      'production_approved': False}, indent=2))


if __name__ == '__main__':
    main()
