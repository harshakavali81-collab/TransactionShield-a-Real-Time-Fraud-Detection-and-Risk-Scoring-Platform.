# Deployment

## Docker local demo
1. From repository root: `python -m pip install -r requirements.txt`.
2. `python scripts/generate_demo.py && python -m ml.training.train && python scripts/create_report.py`.
3. `docker compose up --build -d`.
4. UI: http://localhost:3000; API docs: http://localhost:8000/docs.
5. Shut down: `docker compose down` (preserves PostgreSQL data in a named volume).
6. Optional MLflow: `docker compose --profile tracking up -d mlflow`; for training with logging use `MLFLOW_TRACKING_URI=http://localhost:5000 python -m ml.training.train --tracking`.

## Pure local quickstart
```bash
python -m pip install -r requirements-dev.txt
python scripts/bootstrap.py
uvicorn backend.app.main:app --reload
# Separate terminal
cd frontend && npm install && npm run dev
```
Dashboard <http://localhost:5173>. By default SQLite persists local demonstration prediction history.

## Production deployment checklist (NOT COMPLETED)
- Harden Docker images and dependencies; scan for CVEs and pin hashes.
- Protect with TLS, identity provider, RBAC/tenant boundaries, API gateway and rate limiting.
- Configure secrets and PostgreSQL in managed encrypted storage, add database migrations and backups.
- Restrict CORS, implement observability/audit logs, network policies and runbooks.
- Establish lawful transactions, ground truth verification, delayed-label feedback loop, calibration and drift governance.
- Build a deployment pipeline with artifact signing, staging and rollback; monitoring with service/error budgets.
- Compliance and professional validation before payment-impacting decisions.
