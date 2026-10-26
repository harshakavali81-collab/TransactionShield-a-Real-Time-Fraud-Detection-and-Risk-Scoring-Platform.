"""Bounded, synthetic demo monitoring with explicit evidence limitations."""
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.app.db.session import db_session
from backend.app.db.models import TransactionRecord, ReviewFeedback
from backend.app.services.prediction_service import get_payload
from ml.monitoring.data_drift import evaluate_drift
from ml.monitoring.model_metrics import confirmed_label_metrics

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/overview")
def overview(limit: int = Query(200, ge=10, le=1000), db: Session = Depends(db_session)):
    records = db.scalars(select(TransactionRecord)
                         .order_by(TransactionRecord.created_at.desc()).limit(limit)).all()
    rows = [row.numeric_features for row in records if row.numeric_features]
    try:
        reference = get_payload().get("reference_stats", {})
    except FileNotFoundError:
        reference = {}
    drift = (evaluate_drift(pd.DataFrame(rows), reference) if rows and reference else
             {"status": "insufficient_reference_or_samples", "flagged_features": []})
    return {
        "scope": "synthetic demo predictions only", "sample_count": len(records),
        "feature_samples": len(rows), "model_performance": "unavailable_without_independent_labels",
        "drift": drift, "limitations": [
            "Mean-shift heuristic is not a statistical drift guarantee",
            "Window contains scored requests, not a representative production population",
            "Fraud labels are not supplied by this endpoint",
        ],
    }


class DemoFeedbackIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transaction_id: str = Field(min_length=1, max_length=80)
    review_label: bool
    reviewer_note: str = Field(default="", max_length=300)


@router.post("/demo-feedback", status_code=201)
def record_demo_feedback(item: DemoFeedbackIn, db: Session = Depends(db_session)):
    """For education ONLY. Requires API_KEY when configured; NOT ground truth."""
    if db.get(TransactionRecord, item.transaction_id) is None:
        raise HTTPException(status_code=404, detail="Unknown transaction")
    if db.get(ReviewFeedback, item.transaction_id):
        raise HTTPException(status_code=409, detail="Feedback already recorded")
    db.add(ReviewFeedback(**item.model_dump()))
    db.commit()
    return {"stored": True, "label_provenance": "unverified_demo_reviewer_input"}


@router.get("/demo-feedback-metrics")
def demo_feedback_metrics(db: Session = Depends(db_session)):
    pairs = db.execute(select(ReviewFeedback.review_label, TransactionRecord.is_flagged)
                       .join(TransactionRecord, ReviewFeedback.transaction_id == TransactionRecord.transaction_id)).all()
    if not pairs:
        return {"status": "no_demo_reviews", "count": 0, "not_production_ground_truth": True}
    observed = confirmed_label_metrics([int(p[0]) for p in pairs], [int(p[1]) for p in pairs])
    return {"status": "unverified_demo_review_metrics", "not_production_ground_truth": True, **observed}
