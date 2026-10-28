"""Run a full isolated TransactionShield API demonstration; never uses bank data.

Usage: python scripts/smoke_e2e.py [--report artifacts/reports/smoke_e2e.json]

Creates a new, temporary SQLite database, migrates it with Alembic, and checks
liveness, readiness, authenticated single/batch scoring, duplicate handling,
history, feedback and monitoring. No demo records are retained after exit.
"""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sample(transaction_id, amount=1450.0):
    return {
        "transaction_id": transaction_id, "amount": amount,
        "hour": 3, "account_age_days": 17, "velocity_24h": 4,
        "prior_chargebacks": 0, "ip_risk_score": 0.25,
        "is_international": 0, "is_new_device": 1,
        "merchant_category": "electronics", "transaction_type": "card",
    }


def smoke_run():
    # Must set the env before any project module imports (which read config).
    with tempfile.TemporaryDirectory(prefix="transactionshield-e2e-") as d:
        source = Path(d) / "smoke.sqlite3"
        os.environ["DATABASE_URL"] = f"sqlite:///{source}"
        os.environ["ENVIRONMENT"] = "test"
        os.environ["API_KEY"] = "local-smoke-key-never-use-in-production"
        os.environ["DEMO_RATE_LIMIT"] = "0"
        os.environ["CORS_ORIGINS"] = "http://localhost:5173"
        from alembic import command
        from alembic.config import Config
        from fastapi.testclient import TestClient
        from backend.app.main import app

        alembic = Config(str(ROOT / "alembic.ini"))
        alembic.set_main_option("script_location", str(ROOT / "migrations"))
        command.upgrade(alembic, "head")
        checks = []
        headers = {"X-API-Key": os.environ["API_KEY"]}
        def check(name, condition):
            if not condition:
                raise AssertionError(f"smoke check failed: {name}")
            checks.append(name)

        with TestClient(app) as client:
            check("public health", client.get("/health").status_code == 200)
            check("public readiness", client.get("/ready").status_code == 200)
            check("protected routes reject missing key", client.get("/history").status_code == 401)
            metrics = client.get("/metrics", headers=headers)
            check("protected model metrics", metrics.status_code == 200 and
                  metrics.json().get("dataset") == "synthetic demonstration data")

            first = client.post("/predict", headers=headers, json=sample("smoke_single"))
            check("single scored and stored", first.status_code == 201 and
                  0 <= first.json().get("fraud_probability", -1) <= 1)
            second = client.post("/predict/batch", headers=headers, json={"transactions": [
                sample("smoke_batch_1"), sample("smoke_batch_2", 2900)]})
            check("atomic batch scored", second.status_code == 201 and second.json().get("count") == 2)
            duplicate = client.post("/predict/batch", headers=headers, json={"transactions": [
                sample("smoke_batch_1"), sample("smoke_new") ]})
            check("duplicate batch rejected", duplicate.status_code == 409)
            rows = client.get("/history", headers=headers)
            check("failed batch does not persist", rows.status_code == 200 and len(rows.json()) == 3)
            detail = client.get("/transactions/smoke_single", headers=headers)
            check("audited transaction readable", detail.status_code == 200 and
                  detail.json().get("transaction_id") == "smoke_single")
            feedback = client.post("/monitoring/demo-feedback", headers=headers, json={
                "transaction_id": "smoke_single", "review_label": False,
                "reviewer_note": "Fictional review only",
            })
            check("demo feedback stored", feedback.status_code == 201)
            fm = client.get("/monitoring/demo-feedback-metrics", headers=headers)
            check("demo feedback provenance", fm.status_code == 200 and
                  fm.json().get("not_production_ground_truth") is True)
            monitor = client.get("/monitoring/overview", headers=headers)
            check("monitoring available", monitor.status_code == 200)
            stats = client.get("/statistics", headers=headers)
            check("statistics match stored rows", stats.status_code == 200 and
                  stats.json().get("total_transactions") == 3)
            check("unauthenticated model metrics blocked", client.get("/metrics").status_code == 401)
        # On leaving TemporaryDirectory everything—including feedback—is deleted.
    return {
        "project": "TransactionShield", "scope": "synthetic temporary SQLite demo",
        "status": "passed", "check_count": len(checks), "checks": checks,
        "records_persisted_after_run": 0, "real_financial_data": False,
        "external_bank_integration": False, "production_approved": False,
    }


def main():
    parser = argparse.ArgumentParser(description="Ephemeral, authenticated TransactionShield API smoke test")
    parser.add_argument("--report", type=Path, default=None, help="Optional JSON report output path")
    args = parser.parse_args()
    result = smoke_run()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
