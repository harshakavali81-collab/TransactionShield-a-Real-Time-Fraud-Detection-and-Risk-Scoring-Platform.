# TransactionShield — 7-minute interview demo walkthrough

**Scope:** The data and fraud labels are *synthetic*. This is a software-engineering and ML portfolio application, not a production banking service or real-time card authorization engine.

## Preparation (Python 3.11, local-only)

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/verify_model_artifact.py
alembic upgrade head
pytest -q
uvicorn backend.app.main:app --reload
```

Run `cd frontend && npm install && npm run dev` in another terminal. Open `http://localhost:5173` and `http://localhost:8000/docs`. With Docker Desktop, `docker compose up --build -d` runs the local stack instead. Never use real cardholder or account data.

## Suggested live sequence

1. **README & architecture:** Show the repo structure, system diagram, protected deployment example and synthetic-only disclaimer.
2. **Overview:** Show risk scores and history in React. Explain that the frontend polls at 30-second intervals; it does not pretend to be a streaming bank authorization processor.
3. **Single request:** Use the scoring form or Swagger `POST /predict` to score an entirely fictional transaction. Separate the model's score from rule-based reviewer hints.
4. **Batch scoring:** In Swagger send `POST /predict/batch` with `{"transactions": [{"amount":1500,"hour":2,"account_age_days":10,"velocity_24h":11,"prior_chargebacks":1,"ip_risk_score":0.85,"is_international":1,"is_new_device":1,"merchant_category":"gaming","transaction_type":"card"}]}`. Explain 1–25 inputs, schema validation, generated unique IDs, and all-or-nothing persistence. Re-submit an explicit transaction ID to demonstrate HTTP 409.
5. **Monitoring:** View `/monitoring/overview`. Explain that a mean-shift illustration detects neither true fraud rates nor guaranteed drift; demo feedback is not independently verified ground truth.
6. **Model report:** Open [results](RESULTS.md) and [review-cost sensitivity](DECISION_ANALYSIS.md). Explain test PR-AUC, precision/recall trade-offs, the frozen validation threshold, and low real-world readiness.
7. **Engineering proof:** Open GitHub Actions to show Python tests, React production build, container configuration validation, and exact-commit source archive. Review [security](SECURITY.md) and [production blockers](PRODUCTION_GAP_ANALYSIS.md).

## The strongest honest interview explanation

> I built a reproducible full-stack fraud-risk scoring **demo** with a time-ordered ML evaluation, FastAPI endpoints, transactional SQL persistence, a React dashboard, Docker support, CI checks, and transparent model limitations. The dataset and scored outcomes are synthetic. I implemented atomic batch scoring, request validation, integrity checks, drift illustrations, and scenario charts. The model is not validated for actual bank decisions, so it must remain under human review until prospective real-data testing and independent security assessment are completed.

## Do not claim

Do not say that the project processes a bank's live feed, achieves 99% production fraud accuracy, is independently certified, or is publicly deployed unless separate independent evidence proves it. Never publish passwords, API keys, account numbers or personal data in screenshots or demos.
