"""Exercise a real PostgreSQL-backed *synthetic-only* TransactionShield API.

Safety guard: refuses any database except the dedicated ephemeral CI database.
Run from the repository root after `alembic upgrade head` and with ENVIRONMENT=test.
Never use this command against partner data or an operational database.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
EXPECTED_DB = "transactionshield_ci"


def validate_target(environ=None):
    """Fail closed before importing application modules or accessing the database."""
    from sqlalchemy.engine import make_url

    environ = os.environ if environ is None else environ
    if environ.get("ENVIRONMENT", "") != "test":
        raise RuntimeError("PostgreSQL smoke requires ENVIRONMENT=test")
    url = environ.get("DATABASE_URL", "")
    try:
        parsed = make_url(url)
    except Exception as exc:
        raise RuntimeError("Missing or malformed PostgreSQL smoke DATABASE_URL") from exc
    if not parsed.drivername.startswith("postgresql") or parsed.database != EXPECTED_DB:
        raise RuntimeError("Smoke tests only allow an ephemeral PostgreSQL transactionshield_ci database")
    if not environ.get("API_KEY", ""):
        raise RuntimeError("Smoke test requires a non-empty demo API_KEY")
    return parsed


def smoke_run():
    validate_target()
    from fastapi.testclient import TestClient
    from sqlalchemy import func, select, text
    from backend.app.main import app
    from backend.app.db.session import engine, SessionLocal
    from backend.app.db.models import TransactionRecord, ReviewFeedback
    from scripts.smoke_e2e import sample

    checks = []

    def check(label, truth):
        if not truth:
            raise AssertionError("PostgreSQL smoke check failed: " + label)
        checks.append(label)

    # Test database comes from a fresh, disposable CI postgres:16 service.
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        server_version = conn.execute(text("SHOW server_version")).scalar_one()
    check("Alembic migrated PostgreSQL schema", bool(version))

    headers = {"X-API-Key": os.environ["API_KEY"]}
    with TestClient(app) as client:
        check("Health responds", client.get("/health").status_code == 200)
        check("PostgreSQL readiness responds", client.get("/ready").status_code == 200)
        check("API key protects history", client.get("/history").status_code == 401)
        check("API key protects scoring", client.post("/predict", json=sample("no_key")).status_code == 401)
        first = client.post("/predict", json=sample("ci_postgres_one"), headers=headers)
        check("PostgreSQL single transaction persisted", first.status_code == 201)
        batch = client.post("/predict/batch", headers=headers, json={"transactions": [
            sample("ci_postgres_two"), sample("ci_postgres_three", 2850),
        ]})
        check("Atomic PostgreSQL batch persisted", batch.status_code == 201 and batch.json().get("count") == 2)
        duplicate = client.post("/predict/batch", headers=headers, json={"transactions": [
            sample("ci_postgres_two"), sample("ci_postgres_should_not_exist"),
        ]})
        check("PostgreSQL duplicate batch rolled back", duplicate.status_code == 409)
        scenario = sample("discard_identifier")
        scenario.pop("transaction_id")
        compare = client.post("/simulate/what-if", headers=headers, json={
            "baseline": scenario, "scenario": {**scenario, "amount": 4200.0},
        })
        check("Stateless what-if comparison", compare.status_code == 200 and
              compare.json().get("persisted") is False)
        feedback = client.post("/monitoring/demo-feedback", headers=headers, json={
            "transaction_id": "ci_postgres_one", "review_label": False,
            "reviewer_note": "Synthetic PostgreSQL integration only",
        })
        check("Demo feedback persisted in PostgreSQL", feedback.status_code == 201)
        check("Protected model metrics available", client.get("/metrics", headers=headers).status_code == 200)
        check("Synthetic monitoring available", client.get("/monitoring/overview", headers=headers).status_code == 200)
        stats = client.get("/statistics", headers=headers)
        check("PostgreSQL summary counts match", stats.status_code == 200 and
              stats.json().get("total_transactions") == 3)

    with SessionLocal() as session:
        txn_count = session.scalar(select(func.count()).select_from(TransactionRecord))
        review_count = session.scalar(select(func.count()).select_from(ReviewFeedback))
        rolled_back = session.get(TransactionRecord, "ci_postgres_should_not_exist")
    check("SQLAlchemy PostgreSQL durable records", txn_count == 3 and review_count == 1)
    check("No partial records from rejected batch", rolled_back is None)

    return {
        "project": "TransactionShield", "scope": "isolated CI PostgreSQL synthetic demonstration",
        "status": "passed", "check_count": len(checks), "checks": checks,
        "postgres_major_version": server_version.split(".")[0],
        "records_in_ephemeral_db": txn_count, "real_financial_data": False,
        "production_approved": False, "external_bank_integration": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Synthetic-only disposable PostgreSQL CI smoke")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args(argv)
    report = smoke_run()
    rendered = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
