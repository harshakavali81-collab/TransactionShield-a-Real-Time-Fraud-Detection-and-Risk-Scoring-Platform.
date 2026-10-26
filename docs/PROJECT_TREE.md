# TransactionShield repository tree

The tree below reflects the GitHub source package. Generated synthetic CSVs and local caches are intentionally excluded.

```text
TransactionShield/
  .dockerignore
  .env.example
  .github/workflows/ci.yml
  .gitignore
  Makefile
  README.md
  artifacts/models/.gitkeep
  artifacts/models/fraud_model.joblib
  artifacts/models/metrics.json
  artifacts/reports/.gitkeep
  artifacts/reports/confusion_matrix.png
  artifacts/reports/eda_summary.json
  artifacts/reports/model_comparison.png
  artifacts/reports/precision_recall.png
  artifacts/reports/shap_summary.png
  artifacts/reports/synthetic_amounts.png
  backend/Dockerfile
  backend/__init__.py
  backend/app/__init__.py
  backend/app/api/__init__.py
  backend/app/api/routes/__init__.py
  backend/app/api/routes/analytics.py
  backend/app/api/routes/health.py
  backend/app/api/routes/predict.py
  backend/app/api/routes/transactions.py
  backend/app/core/__init__.py
  backend/app/core/config.py
  backend/app/core/logging_config.py
  backend/app/db/__init__.py
  backend/app/db/models.py
  backend/app/db/repository.py
  backend/app/db/session.py
  backend/app/main.py
  backend/app/schemas/__init__.py
  backend/app/schemas/prediction.py
  backend/app/schemas/transaction.py
  backend/app/services/__init__.py
  backend/app/services/prediction_service.py
  backend/app/services/risk_scoring.py
  backend/tests/test_health.py
  backend/tests/test_predict.py
  backend/tests/test_transactions.py
  data/README.md
  data/interim/.gitkeep
  data/processed/.gitkeep
  data/raw/.gitkeep
  docker-compose.yml
  docs/API_REFERENCE.md
  docs/ARCHITECTURE.md
  docs/DEPLOYMENT.md
  docs/MODEL_CARD.md
  docs/PROJECT_WORKFLOW.md
  docs/TEST_PLAN.md
  docs/screenshots/.gitkeep
  docs/screenshots/transactionshield-architecture.png
  frontend/.dockerignore
  frontend/Dockerfile
  frontend/index.html
  frontend/nginx.conf
  frontend/package.json
  frontend/src/App.jsx
  frontend/src/api/client.js
  frontend/src/components/FraudChart.jsx
  frontend/src/components/MetricCard.jsx
  frontend/src/components/Navbar.jsx
  frontend/src/components/RiskBadge.jsx
  frontend/src/components/TransactionForm.jsx
  frontend/src/components/TransactionTable.jsx
  frontend/src/main.jsx
  frontend/src/pages/Analytics.jsx
  frontend/src/pages/Dashboard.jsx
  frontend/src/pages/ModelPerformance.jsx
  frontend/src/pages/Predict.jsx
  frontend/src/pages/Transactions.jsx
  frontend/src/styles/global.css
  frontend/vite.config.js
  ml/__init__.py
  ml/config.py
  ml/data/__init__.py
  ml/data/feature_engineering.py
  ml/data/generate.py
  ml/data/load_data.py
  ml/data/preprocess.py
  ml/data/validate_data.py
  ml/explainability/__init__.py
  ml/explainability/shap_explainer.py
  ml/monitoring/__init__.py
  ml/monitoring/data_drift.py
  ml/monitoring/model_metrics.py
  ml/training/__init__.py
  ml/training/evaluate.py
  ml/training/save_model.py
  ml/training/train.py
  ml/training/tune.py
  notebooks/01_data_exploration.ipynb
  notebooks/02_data_preprocessing.ipynb
  notebooks/03_baseline_model.ipynb
  notebooks/04_model_comparison.ipynb
  pyproject.toml
  requirements-dev.txt
  requirements.txt
  scripts/__init__.py
  scripts/bootstrap.py
  scripts/create_report.py
  scripts/eda.py
  scripts/generate_demo.py
  scripts/simulate_stream.py
  tests/conftest.py
  tests/test_data.py
  tests/test_explainability.py
  tests/test_pipeline_integration.py
  tests/test_preprocessing.py
  tests/test_training.py
```

See [architecture](ARCHITECTURE.md), [workflow](PROJECT_WORKFLOW.md), and [deployment](DEPLOYMENT.md).


## Upgrade additions (October 2026)
- `migrations/versions/`: versioned legacy-compatible base schema and monitoring upgrade
- `backend/app/api/routes/monitoring.py`: demo drift monitoring, reviewer feedback API
- `frontend/src/pages/Monitoring.jsx`: drift and monitoring interface
- `streaming/producer.py`, `streaming/consumer.py`: optional Kafka-compatible local synthetic stream
- `scripts/check_release.py`: release readiness smoke check
- `scripts/upgrade_legacy_database.py`: backup-gated unversioned schema upgrade
- `docs/SECURITY.md`, `docs/OPERATIONS.md`, `docs/PRODUCTION_GAP_ANALYSIS.md`: operational documentation
