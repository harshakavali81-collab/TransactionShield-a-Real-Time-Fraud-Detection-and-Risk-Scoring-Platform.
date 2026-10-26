import json
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from backend.app.db.session import db_session
from backend.app.db.repository import stats,recent
from backend.app.core.config import METRICS_PATH
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
    return json.loads(METRICS_PATH.read_text()) if METRICS_PATH.exists() else {"status":"unavailable","message":"Run training first"}
