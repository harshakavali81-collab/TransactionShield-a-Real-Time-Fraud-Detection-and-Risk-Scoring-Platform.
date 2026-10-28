"""Plot illustrative review-cost sensitivity from recorded *synthetic* test counts.

NOT real financial costs, an optimal threshold selection, or independent validation.
The existing test confusion matrix is held fixed; no threshold is tuned here.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "artifacts/models/metrics.json"
OUTPUT = ROOT / "artifacts/reports/review_cost_sensitivity.svg"


def cost_scenarios(confusion, missed_costs=(2, 5, 10, 25, 50)):
    if len(confusion) != 2 or any(len(row) != 2 for row in confusion):
        raise ValueError("Expected a 2x2 confusion matrix")
    tn, fp = confusion[0]
    fn, tp = confusion[1]
    if any(type(x) is not int or x < 0 for x in (tn, fp, fn, tp)):
        raise ValueError("Confusion matrix counts must be nonnegative integers")
    if any(x <= 0 for x in missed_costs):
        raise ValueError("Relative missed-case costs must be positive")
    # Each review incurs one hypothetical unit, including true positive reviews.
    # Missed synthetic positives additionally incur a hypothetical penalty.
    return [{"missed_case_penalty_units": cost,
             "review_units": fp + tp,
             "missed_case_units": fn * cost,
             "total_hypothetical_units": fp + tp + fn * cost}
            for cost in missed_costs]


def make_svg(scenarios, *, positive_count):
    width, height, left, top, plot_width, plot_height = 1050, 560, 94, 130, 860, 320
    ymax = max(item["total_hypothetical_units"] for item in scenarios) * 1.10 or 1
    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">',
        '<title id="t">Synthetic fraud-review cost sensitivity</title>',
        '<desc id="d">Fixed holdout confusion matrix under different hypothetical missed-fraud penalty assumptions. Illustrative only, not real loss estimates or threshold optimization.</desc>',
        '<rect width="1050" height="560" rx="18" fill="#0b1731"/>',
        '<text x="40" y="52" fill="#f2f6ff" font-family="Arial, sans-serif" font-size="31" font-weight="700">Review Cost Sensitivity</text>',
        '<text x="40" y="84" fill="#abc2e8" font-family="Arial, sans-serif" font-size="16">Fixed model threshold • synthetic holdout only • illustrative cost units</text>',
    ]
    for fraction in (0, .25, .5, .75, 1):
        y = top + plot_height * (1 - fraction)
        output.append(f'<line x1="{left}" x2="{left+plot_width}" y1="{y:.1f}" y2="{y:.1f}" stroke="#263653" stroke-width="1"/>')
        output.append(f'<text x="{left-15}" y="{y+5:.1f}" text-anchor="end" fill="#abc2e8" font-family="Arial, sans-serif" font-size="13">{round(ymax*fraction)}</text>')
    bar_space = plot_width / len(scenarios)
    for index, item in enumerate(scenarios):
        x = left + bar_space * index + bar_space * .21
        bw = bar_space * .58
        review_height = item["review_units"] / ymax * plot_height
        missed_height = item["missed_case_units"] / ymax * plot_height
        bottom = top + plot_height
        output.append(f'<rect x="{x:.1f}" y="{bottom-review_height:.1f}" width="{bw:.1f}" height="{review_height:.1f}" rx="3" fill="#20bed1"/>')
        output.append(f'<rect x="{x:.1f}" y="{bottom-review_height-missed_height:.1f}" width="{bw:.1f}" height="{missed_height:.1f}" rx="3" fill="#f99465"/>')
        output.append(f'<text x="{x+bw/2:.1f}" y="{bottom-review_height-missed_height-10:.1f}" text-anchor="middle" fill="#ffffff" font-family="Arial, sans-serif" font-size="14" font-weight="700">{item["total_hypothetical_units"]}</text>')
        output.append(f'<text x="{x+bw/2:.1f}" y="{bottom+27:.1f}" text-anchor="middle" fill="#dce7f8" font-family="Arial, sans-serif" font-size="16">{item["missed_case_penalty_units"]}×</text>')
    output.extend([
        '<rect x="218" y="502" width="16" height="16" rx="3" fill="#20bed1"/>',
        '<text x="244" y="516" fill="#cbdcf4" font-family="Arial, sans-serif" font-size="15">Review cost (1 unit per flag)</text>',
        '<rect x="536" y="502" width="16" height="16" rx="3" fill="#f99465"/>',
        '<text x="562" y="516" fill="#cbdcf4" font-family="Arial, sans-serif" font-size="15">Missed positive penalty</text>',
        f'<text x="40" y="547" fill="#8299ba" font-family="Arial, sans-serif" font-size="12">No real banking data • {positive_count} synthetic positive labels • not a financial impact estimate</text>',
        '</svg>',
    ])
    return "\n".join(output) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, default=METRICS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    report = json.loads(args.metrics.read_text(encoding="utf-8"))
    if report.get("dataset") != "synthetic demonstration data":
        raise ValueError("Visualization only supports the approved synthetic demo metrics")
    cm = report["test"]["confusion_matrix"]
    items = cost_scenarios(cm)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(make_svg(items, positive_count=report["test"]["positive_cases"]), encoding="utf-8")
    print("Wrote synthetic-only cost sensitivity chart:", args.output)


if __name__ == "__main__":
    main()
