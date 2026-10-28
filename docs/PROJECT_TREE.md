# TransactionShield repository structure

Generated from source files by `python scripts/generate_project_tree.py`. Generated raw data, local databases, dependency caches, and credentials are excluded.

```text
TransactionShield/
├── .github
│   └── workflows
│       ├── ci.yml
│       └── pages-demo.yml
├── artifacts
│   ├── models
│   │   ├── .gitkeep
│   │   ├── fraud_model.joblib
│   │   ├── metrics.json
│   │   └── model_manifest.json
│   └── reports
│       ├── .gitkeep
│       ├── confusion_matrix.png
│       ├── eda_summary.json
│       ├── end_to_end_smoke.json
│       ├── model_comparison.png
│       ├── precision_recall.png
│       ├── review_cost_sensitivity.svg
│       ├── shap_summary.png
│       └── synthetic_amounts.png
├── backend
│   ├── app
│   │   ├── api
│   │   │   ├── routes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── batch.py
│   │   │   │   ├── health.py
│   │   │   │   ├── monitoring.py
│   │   │   │   ├── predict.py
│   │   │   │   └── transactions.py
│   │   │   └── __init__.py
│   │   ├── core
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── logging_config.py
│   │   │   └── rate_limit.py
│   │   ├── db
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │   └── session.py
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   ├── prediction.py
│   │   │   └── transaction.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── prediction_service.py
│   │   │   └── risk_scoring.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tests
│   │   ├── test_auth.py
│   │   ├── test_batch.py
│   │   ├── test_health.py
│   │   ├── test_metrics_integrity.py
│   │   ├── test_model_fail_closed.py
│   │   ├── test_monitoring.py
│   │   ├── test_predict.py
│   │   ├── test_rate_limit.py
│   │   ├── test_security.py
│   │   └── test_transactions.py
│   ├── __init__.py
│   └── Dockerfile
├── data
│   ├── interim
│   │   └── .gitkeep
│   ├── processed
│   │   └── .gitkeep
│   ├── raw
│   │   └── .gitkeep
│   └── README.md
├── deploy
│   ├── production.env.example
│   └── render.yaml
├── docs
│   ├── screenshots
│   │   ├── .gitkeep
│   │   └── transactionshield-architecture.png
│   ├── visuals
│   │   ├── dashboard-concept.svg
│   │   ├── evaluation-summary.svg
│   │   ├── hero-banner.svg
│   │   ├── model-benchmark.svg
│   │   ├── readiness-roadmap.svg
│   │   └── system-architecture.svg
│   ├── API_REFERENCE.md
│   ├── ARCHITECTURE.md
│   ├── CLOUD_STAGING.md
│   ├── DECISION_ANALYSIS.md
│   ├── DEMO_BACKUP_RECOVERY.md
│   ├── DEMO_DATA_RETENTION.md
│   ├── DEPLOYMENT.md
│   ├── END_TO_END_VERIFICATION.md
│   ├── INDEPENDENT_VALIDATION.md
│   ├── INTEGRATION_CONTRACT.md
│   ├── MODEL_CARD.md
│   ├── MODEL_INTEGRITY.md
│   ├── OPERATIONS.md
│   ├── PORTFOLIO_DEMO.md
│   ├── PRODUCTION_GAP_ANALYSIS.md
│   ├── PROJECT_TREE.md
│   ├── PROJECT_WORKFLOW.md
│   ├── PUBLIC_DEMO.md
│   ├── RELEASE_PROCESS.md
│   ├── RESULTS.md
│   ├── SECURITY.md
│   ├── TEST_PLAN.md
│   └── VISUAL_GALLERY.md
├── frontend
│   ├── src
│   │   ├── api
│   │   │   ├── client.js
│   │   │   └── staticDemo.js
│   │   ├── components
│   │   │   ├── FraudChart.jsx
│   │   │   ├── MetricCard.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── RiskBadge.jsx
│   │   │   ├── TransactionForm.jsx
│   │   │   └── TransactionTable.jsx
│   │   ├── pages
│   │   │   ├── Analytics.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ModelPerformance.jsx
│   │   │   ├── Monitoring.jsx
│   │   │   ├── Predict.jsx
│   │   │   └── Transactions.jsx
│   │   ├── styles
│   │   │   └── global.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── index.html
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
├── migrations
│   ├── versions
│   │   ├── 0001_initial_schema.py
│   │   └── 0002_monitoring_feedback.py
│   └── env.py
├── ml
│   ├── data
│   │   ├── __init__.py
│   │   ├── feature_engineering.py
│   │   ├── generate.py
│   │   ├── load_data.py
│   │   ├── partner_contract.py
│   │   ├── preprocess.py
│   │   └── validate_data.py
│   ├── explainability
│   │   ├── __init__.py
│   │   └── shap_explainer.py
│   ├── monitoring
│   │   ├── __init__.py
│   │   ├── data_drift.py
│   │   └── model_metrics.py
│   ├── training
│   │   ├── __init__.py
│   │   ├── evaluate.py
│   │   ├── independent_validation.py
│   │   ├── model_integrity.py
│   │   ├── save_model.py
│   │   ├── train.py
│   │   └── tune.py
│   ├── __init__.py
│   └── config.py
├── notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_preprocessing.ipynb
│   ├── 03_baseline_model.ipynb
│   └── 04_model_comparison.ipynb
├── scripts
│   ├── __init__.py
│   ├── backup_demo_sqlite.py
│   ├── bootstrap.py
│   ├── check_release.py
│   ├── create_report.py
│   ├── decision_costs.py
│   ├── eda.py
│   ├── generate_demo.py
│   ├── generate_project_tree.py
│   ├── purge_demo_data.py
│   ├── simulate_stream.py
│   ├── smoke_e2e.py
│   ├── upgrade_legacy_database.py
│   ├── validate_partner_feed.py
│   └── verify_model_artifact.py
├── streaming
│   ├── __init__.py
│   ├── consumer.py
│   └── producer.py
├── tests
│   ├── conftest.py
│   ├── test_data.py
│   ├── test_decision_costs.py
│   ├── test_demo_backup.py
│   ├── test_demo_retention.py
│   ├── test_explainability.py
│   ├── test_managed_db_config.py
│   ├── test_migrations.py
│   ├── test_model_integrity.py
│   ├── test_partner_and_holdout.py
│   ├── test_pipeline_integration.py
│   ├── test_preprocessing.py
│   ├── test_streaming.py
│   └── test_training.py
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── README.md
├── requirements-dev.txt
├── requirements-streaming.txt
└── requirements.txt
```

The ML pipeline is under `ml/`, the protected API is under `backend/`, the React interface is under `frontend/`, and independent checks, architecture diagrams, deployment instructions, and reproducible synthetic evaluation evidence are under `tests/`, `docs/`, `.github/`, and `artifacts/`.
