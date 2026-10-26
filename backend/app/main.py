"""FastAPI serving synthetic fraud-risk *demo* predictions."""
import hmac
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import (
    API_KEY, CORS_ORIGINS, ENVIRONMENT, MAX_REQUEST_BYTES, validate_configuration,
)
from backend.app.db.session import init_db
from backend.app.api.routes import health, predict, transactions, analytics, monitoring

logger = logging.getLogger("transactionshield")


@asynccontextmanager
async def lifespan(app):
    validate_configuration()
    # Development convenience only. Production uses Alembic via the container startup command.
    if ENVIRONMENT != "production":
        init_db()
    yield


app = FastAPI(
    title="TransactionShield API", version="1.1.0",
    description="Synthetic educational demonstration; not approved for financial decisions",
    lifespan=lifespan, docs_url=None if ENVIRONMENT == "production" else "/docs",
    redoc_url=None if ENVIRONMENT == "production" else "/redoc",
)
app.add_middleware(
    CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=False,
    allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-API-Key", "X-Request-ID"],
)


@app.middleware("http")
async def guard(request: Request, call_next):
    request_id = str(uuid.uuid4())
    started = time.monotonic()
    status = 500
    try:
        if request.method in {"POST", "PUT", "PATCH"}:
            declared = request.headers.get("content-length")
            if declared and (not declared.isdecimal() or int(declared) > MAX_REQUEST_BYTES):
                response = JSONResponse(status_code=413, content={"detail": "Request too large"})
                response.headers["X-Request-ID"] = request_id
                response.headers["Cache-Control"] = "no-store"
                status = 413
                return response
            # Enforce a real byte cap even if Content-Length was omitted/forged.
            # This demo deliberately accepts only small JSON bodies.
            chunks = []
            byte_count = 0
            async for chunk in request.stream():
                byte_count += len(chunk)
                if byte_count > MAX_REQUEST_BYTES:
                    response = JSONResponse(status_code=413, content={"detail": "Request too large"})
                    response.headers["X-Request-ID"] = request_id
                    response.headers["Cache-Control"] = "no-store"
                    status = 413
                    return response
                chunks.append(chunk)
            request._body = b"".join(chunks)
        public = {"/health", "/ready"}
        if API_KEY and request.url.path not in public:
            supplied = request.headers.get("x-api-key", "")
            if not hmac.compare_digest(supplied, API_KEY):
                response = JSONResponse(status_code=401, content={"detail": "Unauthorized"})
                response.headers["X-Request-ID"] = request_id
                response.headers["Cache-Control"] = "no-store"
                return response
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response
    finally:
        logger.info("request method=%s path=%s status=%d elapsed_ms=%.1f request_id=%s",
                    request.method, request.url.path, status,
                    (time.monotonic() - started) * 1000, request_id)


for route in (health, predict, transactions, analytics, monitoring):
    app.include_router(route.router)
