from fastapi import APIRouter
from backend.app.core.config import MODEL_PATH
router=APIRouter()
@router.get("/health")
def health(): return {"status":"ok","model_ready":MODEL_PATH.exists(),"demo_only":True}
