import json
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import db_session
from backend.app.db.repository import stats,recent
from backend.app.core.config import METRICS_PATH, MODEL_PATH
from ml.training.model_integrity import verify_model_artifacts, ModelIntegrityError
router=APIRouter()
@router.get("/statistics")
def statistics(db:Session=Depends(db_session)):return stats(db)
@router.get("/analytics")
def analytics(db:Session=Depends(db_session)):
    s=stats(db)
    rows=recent(db,500)
    return {"summary":s,"distribution":{t:sum(x.risk_level==t for x in rows) for t in ("LOW","MEDIUM","HIGH")},
        "note":"Distribution represents only the latest 500 predictions; no confirmed fraud labels are available."}
@router.get("/metrics")
def model_metrics():
    try:
        verify_model_artifacts(MODEL_PATH, metrics_path=METRICS_PATH)
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    except (ModelIntegrityError, OSError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=503, detail="Evaluation artifacts unavailable") from exc
