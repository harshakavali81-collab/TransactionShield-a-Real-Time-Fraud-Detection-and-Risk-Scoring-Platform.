"""Configuration for a public synthetic-data demonstration, not banking infrastructure."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parents[3]
def normalize_database_url(url: str) -> str:
    """Managed providers use PostgreSQL URLs without SQLAlchemy's psycopg driver suffix."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url

DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'transactionshield.sqlite3'}"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(ROOT / "artifacts/models/fraud_model.joblib")))
METRICS_PATH = Path(os.getenv("METRICS_PATH", str(ROOT / "artifacts/models/metrics.json")))
CORS_ORIGINS = [v.strip() for v in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") if v.strip()]
API_KEY = os.getenv("API_KEY", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
MAX_REQUEST_BYTES = int(os.getenv("MAX_REQUEST_BYTES", "16384"))
DEMO_RATE_LIMIT = int(os.getenv("DEMO_RATE_LIMIT", "0"))  # per minute, per process, 0 disables


def validate_configuration():
    """Refuse to serve unprotected public deployments by accident."""
    if not 0 <= DEMO_RATE_LIMIT <= 10000:
        raise RuntimeError("DEMO_RATE_LIMIT must be 0..10000 requests per minute")
    if ENVIRONMENT not in {"development", "test", "staging", "production"}:
        raise RuntimeError("ENVIRONMENT must be development, test, staging, or production")
    if not 1024 <= MAX_REQUEST_BYTES <= 1048576:
        raise RuntimeError("MAX_REQUEST_BYTES must be between 1024 and 1048576")
    if ENVIRONMENT in {"staging", "production"}:
        if len(API_KEY) < 32:
            raise RuntimeError("Staging/production requires a random API_KEY of at least 32 characters")
        if any(v == "*" or v.startswith("http://") for v in CORS_ORIGINS):
            raise RuntimeError("Staging/production requires explicit HTTPS CORS origins")
        if DATABASE_URL.startswith("sqlite:"):
            raise RuntimeError("Staging/production requires a managed PostgreSQL database")
        if not MODEL_PATH.exists():
            raise RuntimeError("Trained model unavailable")
        if not METRICS_PATH.is_file():
            raise RuntimeError("Staging/production requires model evaluation metadata")
        if DEMO_RATE_LIMIT <= 0:
            raise RuntimeError("Staging/production requires an enabled per-instance demo rate limit")
    if ENVIRONMENT == "production":
        # This repository ships only a synthetic, unapproved demonstration model.
        raise RuntimeError(
            "Synthetic demonstration model is prohibited in production; "
            "use protected staging for fictional traffic only"
        )
