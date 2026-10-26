# External model validation (evidence tool, **not certification**)

The shipped model was trained on synthetic data. No trustworthy statement about performance on real bank transactions can be made from those synthetic scores.

An authorized evaluator can run a separately acquired, independently labeled test set **locally** without changing model weights or the validation-derived decision threshold:

```bash
python -m ml.training.independent_validation \
  --csv /secure/authorized_labeled_holdout.csv \
  --data-approved \
  --provenance "Institution-approved adjudicated labels, outcomes observed for 90 days" \
  --output /secure/report.json
```

The script checks a strict, PII-minimized feature schema, duplicates, time fields, both label classes, and the minimum sample size. It rejects the bundled `DEMO-` synthetic IDs. It creates aggregate PR-AUC, ROC-AUC, precision, recall, F1, Brier score, confusion matrix, and threshold, plus exploratory bootstrap uncertainty intervals and cohort assessments for merchant and transaction type. Scores use the **frozen** trained model, not a model fitted to the holdout. The report contains a SHA-256 digest of the model, counts and operator-supplied provenance declaration but **never raw event rows**.

## Important limitations

- Source ownership, authorization, label independence and accuracy are **operator attestations**, not independently established by this code.
- A confidence interval around poor performance does not fix performance. The bootstrap does not account for time dependence, linked customers, delayed outcomes, class shift or sampling bias.
- Deploy only after qualified owners define fraud-lift/false-positive costs, minimum acceptable recall/PR-AUC and group-level harms, validate on representative out-of-time and out-of-institution datasets, calibrate probabilities, and approve a human review fallback.
- Never commit real labeled holdout datasets, private reports, credentials, or bank agreement terms to a public GitHub repository.
- This tool is **not PCI DSS certification, penetration testing, legal review, SOC 2, or live banking approval**.
