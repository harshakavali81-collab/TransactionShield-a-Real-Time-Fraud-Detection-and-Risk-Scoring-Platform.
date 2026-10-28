"""Atomic batch predictions for synthetic demonstration data only.

No uploaded customer data, partial success, or automatic financial decision is supported.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.db.models import TransactionRecord
from backend.app.db.session import db_session
from backend.app.schemas.transaction import TransactionIn
from backend.app.services.prediction_service import score
from ml.config import NUMERIC
from ml.training.model_integrity import ModelIntegrityError

router = APIRouter(tags=["synthetic batch demo"])


class BatchIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transactions: list[TransactionIn] = Field(min_length=1, max_length=25)


@router.post("/predict/batch", status_code=201)
def predict_batch(batch: BatchIn, db: Session = Depends(db_session)):
    """Score and save 1–25 transactions in one database transaction.

    Any duplicate identifier, scoring failure, or invalid input rejects the
    entire batch; it must never partially persist successful predictions.
    """
    identifiers = [item.transaction_id or str(uuid.uuid4()) for item in batch.transactions]
    if len(set(identifiers)) != len(identifiers):
        raise HTTPException(409, "Duplicate transaction_id within batch")

    existing = db.scalars(
        select(TransactionRecord.transaction_id).where(TransactionRecord.transaction_id.in_(identifiers))
    ).first()
    if existing is not None:
        raise HTTPException(409, "One or more transaction_id values already exist")

    results = []
    try:
        for item, identifier in zip(batch.transactions, identifiers):
            prediction = score(item)
            record = TransactionRecord(
                transaction_id=identifier,
                amount=item.amount,
                numeric_features={key: getattr(item, key) for key in NUMERIC},
                **prediction,
            )
            db.add(record)
            results.append((record, prediction))
        db.commit()
    except (FileNotFoundError, ModelIntegrityError) as exc:
        db.rollback()
        raise HTTPException(503, "Demo model unavailable") from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "One or more transaction_id values already exist") from exc

    return {
        "count": len(results),
        "demo_only": True,
        "results": [
            {"transaction_id": rec.transaction_id, "created_at": rec.created_at, **prediction}
            for rec, prediction in results
        ],
    }
