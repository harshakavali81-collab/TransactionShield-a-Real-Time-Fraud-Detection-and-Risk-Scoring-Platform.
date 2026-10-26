from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import CORS_ORIGINS,API_KEY
from backend.app.db.session import init_db
from backend.app.api.routes import health,predict,transactions,analytics
@asynccontextmanager
async def lifespan(app):
    init_db()
    yield
app=FastAPI(title="TransactionShield API",version="1.0.0",description="Synthetic demonstration; not a payment fraud production service",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=CORS_ORIGINS,allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["Content-Type","X-API-Key"])
@app.middleware("http")
async def guard(request:Request,call_next):
    if API_KEY and request.url.path not in ("/health","/openapi.json","/docs","/redoc"):
        if request.headers.get("x-api-key")!=API_KEY:return JSONResponse(status_code=401,content={"detail":"Invalid API key"})
    return await call_next(request)
app.include_router(health.router)
app.include_router(predict.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
