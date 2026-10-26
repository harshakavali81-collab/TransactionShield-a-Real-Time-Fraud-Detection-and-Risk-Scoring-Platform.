from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.orm import Session
from backend.app.db.session import db_session
from backend.app.db.models import TransactionRecord
from backend.app.db.repository import recent
router=APIRouter()
def to_dict(rec):
    return {"transaction_id":rec.transaction_id,"created_at":rec.created_at,"amount":rec.amount,
        "fraud_probability":rec.fraud_probability,"risk_score":rec.risk_score,
        "risk_level":rec.risk_level,"is_flagged":rec.is_flagged,"model_version":rec.model_version,"reasons":rec.reasons}
@router.get("/history")
def history(limit:int=Query(50,ge=1,le=500),db:Session=Depends(db_session)):
    return [to_dict(x) for x in recent(db,limit)]
@router.get("/transactions/{transaction_id}")
def transaction_detail(transaction_id:str,db:Session=Depends(db_session)):
    rec=db.get(TransactionRecord,transaction_id)
    if rec is None:raise HTTPException(404,"Transaction not found")
    return to_dict(rec)
