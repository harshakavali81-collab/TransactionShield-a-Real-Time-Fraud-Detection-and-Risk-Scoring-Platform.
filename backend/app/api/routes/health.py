"""Separate process liveness from model and database readiness."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from backend.app.core.config import MODEL_PATH, METRICS_PATH
from ml.training.model_integrity import verify_model_artifacts, ModelIntegrityError
from backend.app.db.session import engine

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "model_ready": MODEL_PATH.is_file(), "demo_only": True}


@router.get("/ready")
def ready():
    db_ok = False
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM transactions LIMIT 1"))
        db_ok = True
    except Exception:
        pass
    try:
        verify_model_artifacts(MODEL_PATH, metrics_path=METRICS_PATH)
        model_ok = True
    except (ModelIntegrityError, OSError):
        model_ok = False
    status = 200 if db_ok and model_ok else 503
    return JSONResponse(status_code=status, content={
        "status": "ready" if status == 200 else "unavailable",
        "database_ready": db_ok, "model_ready": model_ok, "demo_only": True,
    })
