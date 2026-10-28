"""Stateless, educational what-if comparison for synthetic transaction attributes.

Changes in a model score are not causal explanations or fraud outcomes.
This endpoint never records either transaction or its comparison.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, model_validator

from backend.app.schemas.transaction import TransactionIn
from backend.app.services.prediction_service import score
from ml.training.model_integrity import ModelIntegrityError

router = APIRouter(tags=["synthetic what-if simulation"])


class ScenarioPair(BaseModel):
    model_config = ConfigDict(extra="forbid")
    baseline: TransactionIn
    scenario: TransactionIn

    @model_validator(mode="after")
    def ensure_anonymous_examples(self):
        if self.baseline.transaction_id is not None or self.scenario.transaction_id is not None:
            raise ValueError("What-if examples cannot include transaction_id")
        return self


@router.post("/simulate/what-if")
def compare_scenarios(pair: ScenarioPair):
    """Compare scores without any database writes or asserted causal effects."""
    try:
        base = score(pair.baseline)
        scenario = score(pair.scenario)
    except (FileNotFoundError, ModelIntegrityError) as exc:
        raise HTTPException(status_code=503, detail="Demo model unavailable") from exc

    if base["model_version"] != scenario["model_version"]:
        raise HTTPException(status_code=503, detail="Scoring model inconsistent")

    before = pair.baseline.model_dump(exclude={"transaction_id"})
    after = pair.scenario.model_dump(exclude={"transaction_id"})
    delta = round(scenario["fraud_probability"] - base["fraud_probability"], 6)
    return {
        "demo_only": True,
        "persisted": False,
        "baseline": base,
        "scenario": scenario,
        "changed_features": sorted(key for key in before if before[key] != after[key]),
        "delta_probability": delta,
        "delta_risk_score": scenario["risk_score"] - base["risk_score"],
        "flag_changed": bool(base["is_flagged"] != scenario["is_flagged"]),
        "direction": "increase" if delta > 0 else "decrease" if delta < 0 else "unchanged",
        "disclaimer": "Synthetic model scores only; differences are associations, not causal effects, actual fraud probabilities, or payment decisions.",
    }
