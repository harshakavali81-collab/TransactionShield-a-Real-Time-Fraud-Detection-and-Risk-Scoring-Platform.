"""Validated prediction with an idempotency key and a committed audit record."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.schemas.transaction import TransactionIn
from backend.app.db.session import db_session
from backend.app.db.models import TransactionRecord
from backend.app.services.prediction_service import score
from ml.config import NUMERIC

router = APIRouter()


@router.post("/predict", status_code=201)
def predict(txn: TransactionIn, db: Session = Depends(db_session)):
    identifier = txn.transaction_id or str(uuid.uuid4())
    if db.get(TransactionRecord, identifier):
        raise HTTPException(status_code=409, detail="transaction_id already exists")
    try:
        result = score(txn)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    numeric = {key: getattr(txn, key) for key in NUMERIC}
    record = TransactionRecord(transaction_id=identifier, amount=txn.amount,
                               numeric_features=numeric, **result)
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="transaction_id already exists") from exc
    return {"transaction_id": identifier, "created_at": record.created_at, **result}
