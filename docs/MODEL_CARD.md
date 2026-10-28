# Model card — TransactionShield synthetic demo

**Intended use:** educational end-to-end ML and dashboard demonstration, job interviews and software engineering practice. **Not intended for:** real financial decisions, automated blocks, customer profiling, or claims about actual fraud prevalence.

**Data:** 4,000 generated records, fixed RNG seed and simulated probabilistic fraud labels. Features: amount, hour, account age, velocity, chargeback count, proxy IP risk, cross-border and new-device indicators, merchant category, transaction type. No real individuals or financial account information are present.

**Learning:** time-ordered 60/20/20 train/validation/test split; transformations fit only on train. Candidate learners include class-weighted logistic regression/random forest and optional XGBoost/LightGBM. Ranking by validation PR-AUC; F2 threshold tuned only on validation. `artifacts/models/metrics.json` holds the actual metrics after training, with a held-out test confusion matrix and PR-AUC. Never invent accuracy, AUC, or recall values. A deterministic synthetic generator may still create unrealistic shifts across time.

**Evaluation:** positive-case count, precision, recall, F1, PR-AUC, ROC-AUC, Brier score, confusion matrix. The fraud dataset is entirely artificial and synthetic test accuracy is not transferable to real transactions. Most importantly, PR-AUC depends on the fraud base rate. Sampling assumptions and unknown fraud investigation costs make naive comparisons unreliable.

**Interpretability:** SHAP summary may be computed for compatible tree estimators if SHAP is installed. Dashboard "reasons" are transparent hand-authored review heuristics, NOT model-derived attribution or causal effects. UI intentionally labels them that way.

**Safety / governance:** no real-world use without expert model review, calibration, fairness and disparate-impact checks where appropriate, confirmed-label evaluation, protection from PII collection, adversarial threat modeling, audit access control, model version tracking, documentation of data provenance and human oversight.

## Separate rolling-origin baseline

The [five-fold chronological diagnostic](ROLLING_VALIDATION.md) uses a fixed logistic regression model with thresholds tuned on each fold’s validation period only. It is not an independent production validation of the served LightGBM model.
