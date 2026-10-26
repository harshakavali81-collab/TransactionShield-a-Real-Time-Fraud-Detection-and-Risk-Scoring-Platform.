import joblib
from ml.config import MODEL

def save_model(payload,path=MODEL):
    path.parent.mkdir(parents=True,exist_ok=True)
    joblib.dump(payload,path)

def load_model(path=MODEL):
    return joblib.load(path)
