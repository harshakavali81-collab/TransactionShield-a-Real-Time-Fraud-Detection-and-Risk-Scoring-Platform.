"""Separate process liveness from model and database readiness."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from backend.app.core.config import MODEL_PATH
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
    model_ok = MODEL_PATH.is_file()
    status = 200 if db_ok and model_ok else 503
    return JSONResponse(status_code=status, content={
        "status": "ready" if status == 200 else "unavailable",
        "database_ready": db_ok, "model_ready": model_ok, "demo_only": True,
    })
