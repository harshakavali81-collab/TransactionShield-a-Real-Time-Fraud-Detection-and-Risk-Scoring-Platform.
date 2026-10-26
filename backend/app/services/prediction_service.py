from functools import lru_cache
import pandas as pd
from backend.app.core.config import MODEL_PATH
from backend.app.services.risk_scoring import level,reasons_for_features
from ml.training.save_model import load_model
@lru_cache(maxsize=1)
def get_payload():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("No trained model. Run python -m ml.training.train first.")
    return load_model(MODEL_PATH)

def score(txn):
    d=txn.model_dump(exclude={"transaction_id"})
    payload=get_payload()
    probability=float(payload["pipeline"].predict_proba(pd.DataFrame([d]))[0,1])
    return {"fraud_probability":round(probability,6),"risk_score":round(probability*100),
       "risk_level":level(probability),"is_flagged":probability>=payload["threshold"],
       "model_version":payload["model_name"],"reasons":reasons_for_features(d)}
