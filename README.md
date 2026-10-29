# 🛡️ TransactionShield — Real-Time Fraud Detection & Risk Scoring Platform

Score synthetic transactions, inspect model evaluation, and review risk signals through a FastAPI service and React dashboard.

[Setup](#local-installation--setup-guide) · [Architecture](#architecture--system-design-diagram) · [Detailed guide](PROJECT_GUIDE.md) · [Repository standard](docs/REPOSITORY_STANDARD.md)

## Visuals

![Branded TransactionShield project banner](<docs/visuals/hero-banner.svg>)

Existing project visual; diagrams and illustrative graphics are not evidence of a deployed application.

## Live Link / Demo

Run the local demo using the setup guide below. No public deployment URL has been verified for this documentation update.

## Key Features

TransactionShield scores synthetic credit card, wallet, transfer, and e-commerce transaction attributes. A fitted classifier estimates a fraud score; configurable rule-based review hints complement (but do **not** explain) the model. The REST API persists scored transactions and a responsive React dashboard visualizes review flags, history, risk distribution, and measured synthetic test metrics. The dashboard refreshes every 30 seconds; this is polling rather than a stream processor.

### Features
- Deterministic synthetic transaction generation and validation, without real financial data.
- Leakage-safe scikit-learn preprocessing; **chronological** train/validation/test evaluation.
- Logistic Regression, Random Forest and optional XGBoost/LightGBM comparison by **validation PR-AUC**.
- Independent validation F2 threshold selection; held-out precision, recall, F1, PR-AUC, ROC-AUC, Brier score and confusion matrix.
- Five-fold expanding-window diagnostic with a fixed logistic baseline, per-fold validation thresholds and chart (all fictional data).
- Optional tree SHAP summary function and MLflow tracking. UI review hints are separate explicit rules.
- FastAPI: `/predict`, `/history`, `/transactions/{id}`, `/statistics`, `/analytics`, `/metrics`, `/health`, and `/docs`.
- Pydantic constraints, duplicate transaction ID protection, SQLite development fallback, PostgreSQL Docker service.
- Optional bounded per-peer demonstration rate limiting (`DEMO_RATE_LIMIT`, HTTP 429 with `Retry-After`); **not** a production gateway.
- React / Recharts: Overview, Scoring, Transactions with CSV export, Analytics, Model Performance.
- Tests, architecture docs, workflows, reproducible charts, Docker Compose, local simulator.
- Ephemeral authenticated end-to-end API smoke check with 14 cross-component assertions and zero persisted customer or test data.
- Guarded SQLite-only synthetic backup demonstration with dry-run, schema checks, no overwrite, and verified snapshot counts.
- Alembic migration, readiness checks, request-security guardrails, drift monitoring API and React monitoring tab.
- Optional Kafka-compatible synthetic producer/consumer with at-least-once offset commits.
- Clear demo-review feedback provenance and operational deployment/security runbooks.

## Tech Stack

![Python](https://img.shields.io/badge/Python-334155?style=flat-square) ![FastAPI](https://img.shields.io/badge/FastAPI-334155?style=flat-square) ![scikit-learn](https://img.shields.io/badge/scikit--learn-334155?style=flat-square) ![Pandas](https://img.shields.io/badge/Pandas-334155?style=flat-square) ![NumPy](https://img.shields.io/badge/NumPy-334155?style=flat-square) ![React](https://img.shields.io/badge/React-334155?style=flat-square) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-334155?style=flat-square) ![LightGBM](https://img.shields.io/badge/LightGBM-334155?style=flat-square)

Dependency versions and optional packages are defined in the repository manifests.

## Architecture / System Design Diagram

[Architecture documentation / diagram](<docs/ARCHITECTURE.md>)

## Local Installation & Setup Guide

```bash
git clone https://github.com/harshakavali81-collab/TransactionShield-a-Real-Time-Fraud-Detection-and-Risk-Scoring-Platform..git
cd TransactionShield-a-Real-Time-Fraud-Detection-and-Risk-Scoring-Platform.
```

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/generate_demo.py
python -m ml.training.train
python scripts/verify_model_artifact.py
python scripts/create_report.py
pytest -q
uvicorn backend.app.main:app --reload
```
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```
React: http://localhost:5173 · API documentation: http://localhost:8000/docs

Or run `docker compose up --build -d` after training for PostgreSQL + React/Nginx + API (UI: http://localhost:3000). Optional MLflow tracking via `docker compose --profile tracking up -d mlflow` and `MLFLOW_TRACKING_URI=http://localhost:5000 python -m ml.training.train --tracking`.

## Challenges & Solutions

Fraud evaluation can overstate performance when future information leaks into training or thresholds are tuned on the test set. The documented workflow uses chronological splits, validation-based model/threshold selection and a separate held-out evaluation. Review hints remain explicit rules rather than explanations of the classifier.

## Future Improvements

- **Implemented:** Synthetic data, ML model comparisons, risk scoring, SQL persistence, REST API, responsive React dashboard, CI, Docker, documentation.
- **Implemented expansion:** Initial Alembic schema, health/readiness, synthetic drift monitoring and bounded review feedback, security defaults, monitoring UI, optional Kafka-compatible demo integration.
- **Implemented evaluation/deployment expansion:** strict authorized CSV contract, frozen-model external holdout report with bootstrap intervals, streaming request-byte ceiling, offline static React preview, Pages publishing workflow, and optional Render API+PostgreSQL staging blueprint. These require real owner configuration to publish/run.
- **Production blockers:** Consented labeled data and validation, calibration, tenant-aware identity, encryption and gateway policies, real backup/restore, hosted cloud infrastructure, managed event ingestion, independent audits, monitoring alerts and operational approvals. These cannot be claimed complete.

## Scope and supporting evidence

> **Portfolio/demo application** · Machine learning + FastAPI + React + SQLAlchemy/PostgreSQL + Docker + optional MLflow and SHAP. **Data, predictions, and evaluation are synthetic. This is not a production fraud detector.**

## Repository Structure

| Location | Purpose |
| --- | --- |
| `backend/` | Backend services |
| `frontend/` | Frontend interface |
| `tests/` | Tests |
| `docs/` | Documentation |
| `data/` | Data and samples |
| `scripts/` | Automation scripts |
| `.github/` | Issue forms, PR template and automated checks |

[Complete file inventory and workflow](docs/REPOSITORY_STANDARD.md). Runtime entry points retain their existing paths.

## Workflow & Tracking

Use the [bug and feature forms](https://github.com/harshakavali81-collab/TransactionShield-a-Real-Time-Fraud-Detection-and-Risk-Scoring-Platform./issues/new/choose) to define work with acceptance criteria. Keep tasks in Todo → In progress → Review → Done, and link a pull request with `Closes #<number>`. See [the maintenance workflow](docs/REPOSITORY_STANDARD.md#workflow).

## License

Original project software is available under the [MIT License](LICENSE). See [licensing scope](docs/LICENSING.md) for third-party and data exclusions.

