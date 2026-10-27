# TransactionShield — Visual Gallery

**All evaluation numbers are measured on synthetic transactions**, drawn from [saved metrics](../artifacts/models/metrics.json). These images do not claim deployment, real banking performance or security certification.

## Branded hero

![Brand banner](visuals/hero-banner.svg)

## Dashboard concept

![Static dashboard concept](visuals/dashboard-concept.svg)

A design mockup using real recorded **synthetic** evaluation values; it is not a screenshot of a deployed application.

## Architecture

![Pipeline and human-review system](visuals/system-architecture.svg)

See the [original detailed reference image](screenshots/transactionshield-architecture.png).

## Model benchmark

![Measured validation PR-AUC](visuals/model-benchmark.svg)

These are validation comparison scores. The separate held-out test PR-AUC is displayed below the graph, not substituted for the validation metric.

## Honest evaluation

![Synthetic held-out confusion matrix](visuals/evaluation-summary.svg)

True negatives: 660; false positives: 119; false negatives: 18; true positives: 3. All correspond to the held-out synthetic evaluation.

## Readiness

![Demo readiness versus external requirements](visuals/readiness-roadmap.svg)

Independent validation, production hosting and real banking integration remain external requirements.

These diagrams are portable SVG files with accessible titles and no external script dependencies. Update metric-based captions if metrics.json changes.
