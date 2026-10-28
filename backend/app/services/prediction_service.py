import math
from functools import lru_cache
import pandas as pd
from backend.app.core.config import MODEL_PATH
from backend.app.services.risk_scoring import level,reasons_for_features
from ml.training.save_model import load_model
from ml.training.model_integrity import ModelIntegrityError
@lru_cache(maxsize=1)
def get_payload():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("No trained model. Run python -m ml.training.train first.")
    return load_model(MODEL_PATH)

def score(txn):
    d=txn.model_dump(exclude={"transaction_id"})
    payload=get_payload()
    try:
        probability=float(payload["pipeline"].predict_proba(pd.DataFrame([d]))[0,1])
    except (ValueError, TypeError, IndexError, KeyError) as exc:
        raise ModelIntegrityError("Model cannot score the input schema") from exc
    if not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ModelIntegrityError("Model returned invalid probability")
    return {"fraud_probability":round(probability,6),"risk_score":round(probability*100),
       "risk_level":level(probability),"is_flagged":probability>=payload["threshold"],
       "model_version":payload["model_name"],"reasons":reasons_for_features(d)}
