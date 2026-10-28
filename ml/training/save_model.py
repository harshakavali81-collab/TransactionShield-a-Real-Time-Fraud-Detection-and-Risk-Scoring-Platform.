from pathlib import Path
import joblib
from ml.training.model_integrity import verify_model_artifacts
from ml.config import MODEL

def save_model(payload,path=MODEL):
    path.parent.mkdir(parents=True,exist_ok=True)
    joblib.dump(payload,path)

def load_model(path=MODEL):
    verify_model_artifacts(Path(path))
    return joblib.load(path)
