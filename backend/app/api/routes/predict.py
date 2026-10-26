import uuid
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.schemas.transaction import TransactionIn
from backend.app.db.session import db_session
from backend.app.db.models import TransactionRecord
from backend.app.services.prediction_service import score
router=APIRouter()
@router.post("/predict",status_code=201)
def predict(txn:TransactionIn,db:Session=Depends(db_session)):
    identifier=txn.transaction_id or str(uuid.uuid4())
    if db.get(TransactionRecord,identifier):raise HTTPException(status_code=409,detail="transaction_id already exists")
    try: out=score(txn)
    except FileNotFoundError as e:raise HTTPException(status_code=503,detail=str(e)) from e
    rec=TransactionRecord(transaction_id=identifier,amount=txn.amount,**out)
    db.add(rec)
    try:db.commit();db.refresh(rec)
    except IntegrityError as e:db.rollback();raise HTTPException(status_code=409,detail="transaction_id already exists") from e
    return {"transaction_id":identifier,"created_at":rec.created_at,**out}
