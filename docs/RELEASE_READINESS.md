# Release evidence: portfolio demonstration vs. real-world fraud decisions

`python scripts/release_readiness.py --output artifacts/reports/release_readiness.json` produces a reproducible JSON statement about what **this repository** can establish.

- A valid model digest means the checked-in synthetic artifact matches its manifest. It is **not** a signature, security audit, independent validation, or proof of model quality.
- The stored test metrics were measured on generated **synthetic** records. The model recorded 3.19% precision-recall AUC and 14.29% recall on its original 800-record holdout, with 21 synthetic positives. These figures do not generalize to real banking.
- `production_release_approved` is always `false`. No command or CI run can promote the synthetic model for financial decision-making.
- The protected Render Blueprint is `ENVIRONMENT=staging`; the app refuses this synthetic model in `production`.
- Staging requires a secret API key, explicit HTTPS CORS origins, PostgreSQL, a positive per-instance demo request limit, and a model artifact. Gateway identity, multi-tenant authorization, monitoring, backups, and external review remain requirements for sensitive use.
- The public GitHub Pages preview uses **offline fictional rules**, not the actual ML model or backend. Pages must be enabled separately by the repository owner.

## Independent external gates (not met by this repository)

1. Authorized, representative transactions; minimal collection; labeling provenance; verified outcomes.
2. Frozen-model real holdout validation, calibration, confidence and subgroup stability, cost studies and human review.
3. Hosted identity-aware infrastructure, authorization controls, monitoring, alerting, and verified recovery.
4. Independent legal, compliance and security approval for the jurisdiction and financial-use case.

**Source-code checks and CI cannot establish a banking certification, live service or real-world fraud effectiveness.**
