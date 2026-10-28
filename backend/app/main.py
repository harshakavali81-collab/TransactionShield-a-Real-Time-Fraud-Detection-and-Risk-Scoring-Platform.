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
    API_KEY, CORS_ORIGINS, ENVIRONMENT, MAX_REQUEST_BYTES, DEMO_RATE_LIMIT,
    validate_configuration,
)
from backend.app.core.rate_limit import TokenBucketLimiter
from backend.app.db.session import init_db
from backend.app.api.routes import health, predict, transactions, analytics, monitoring, batch

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


rate_limiter = TokenBucketLimiter()


@app.middleware("http")
async def guard(request: Request, call_next):
    request_id = str(uuid.uuid4())
    started = time.monotonic()
    status = 500

    def reject(code: int, detail: str, retry_after: int = 0):
        response = JSONResponse(status_code=code, content={"detail": detail})
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        if retry_after:
            response.headers["Retry-After"] = str(retry_after)
        return response

    try:
        path = request.url.path
        public = path in {"/health", "/ready"}
        preflight = request.method == "OPTIONS"

        # Reject declared oversized requests without consuming memory.
        if request.method in {"POST", "PUT", "PATCH"}:
            declared = request.headers.get("content-length")
            if declared and (not declared.isdecimal() or int(declared) > MAX_REQUEST_BYTES):
                status = 413
                return reject(413, "Request too large")

        # Per-peer in-memory demo limiter, not per-account or distributed.
        # Never trust arbitrary X-Forwarded-For client-supplied headers.
        if not public and not preflight and DEMO_RATE_LIMIT > 0:
            peer = request.client.host if request.client else "unknown"
            retry_after = rate_limiter.consume(peer, DEMO_RATE_LIMIT)
            if retry_after:
                status = 429
                return reject(429, "Demo request limit exceeded", retry_after)

        if API_KEY and not public and not preflight:
            supplied = request.headers.get("x-api-key", "")
            if not hmac.compare_digest(supplied, API_KEY):
                status = 401
                return reject(401, "Unauthorized")

        if request.method in {"POST", "PUT", "PATCH"}:
            # Cap streamed and transfer-encoded bodies too.
            chunks = []
            byte_count = 0
            async for chunk in request.stream():
                byte_count += len(chunk)
                if byte_count > MAX_REQUEST_BYTES:
                    status = 413
                    return reject(413, "Request too large")
                chunks.append(chunk)
            request._body = b"".join(chunks)

        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response
    finally:
        logger.info(
            "request method=%s path=%s status=%d elapsed_ms=%.1f request_id=%s",
            request.method, request.url.path, status,
            (time.monotonic() - started) * 1000, request_id,
        )

for route in (health, predict, transactions, analytics, monitoring, batch):
    app.include_router(route.router)
