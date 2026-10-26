# Data and application workflow

1. **Generate or securely collect data:** `python scripts/generate_demo.py` creates synthetic example transactions without personal information. A real project must use lawfully collected and properly consented historical data.
2. **Validate:** `ml/data/validate_data.py` checks presence, numeric range, nulls and labels.
3. **Preprocess:** train-fitted median imputers/standardization and one-hot encoding prevent fitting transformations on the test set; unrecognized categorical values are ignored, not errors.
4. **Train:** `python -m ml.training.train` creates time-ordered training, validation and test samples. Logistic regression, random forest, and optionally XGBoost and LightGBM are evaluated.
5. **Select:** validation PR-AUC determines model; validation F2 determines the review threshold; final metrics use the held-out test split.
6. **Explain:** optional SHAP summary via `ml/explainability/shap_explainer.py`; deterministic rule-based UI hints are distinct from attribution estimates.
7. **Score:** `/predict` validates a new transaction, computes a probability and risk score 0-100 and saves an idempotent transaction ID.
8. **Review:** React surfaces scores, review flags, analytics and performance, with download of transaction history as CSV.
9. **Test:** pytest verifies data behavior, risk scoring, error handling, endpoint response, duplicate IDs, and model availability. GitHub Actions builds both Python backend and React.
10. **Observe:** confirmed-labeled real-world model monitoring remains future work because demo predictions do not have ground-truth fraud outcomes.

**Note:** A higher model score triggers *review*, not an automatic payment rejection. Risk category boundaries (LOW < 0.30, MEDIUM 0.30–0.65, HIGH >= 0.65) are demonstration policy values; review flags use a *separately validation-tuned* decision threshold.
