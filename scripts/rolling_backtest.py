"""Reproduce a synthetic time-ordered evaluation; never touch the serving model."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.data.generate import create_synthetic
from ml.training.rolling_validation import rolling_origin_report


def save_diagnostics(report: dict, json_path: Path, chart_path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    json_path.parent.mkdir(parents=True, exist_ok=True)
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    folds = report["folds"]
    x = [f["fold"] for f in folds]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x, [f["pr_auc"] for f in folds], marker="o", label="Test PR-AUC")
    ax.plot(x, [f["recall"] for f in folds], marker="s", label="Test recall (validation threshold)")
    ax.set(xlabel="Rolling-origin fold (chronological)", ylabel="Score (0–1)",
           title="TransactionShield • Synthetic rolling-origin diagnostics")
    ax.set_ylim(0, 1)
    ax.set_xticks(x)
    ax.grid(alpha=0.2)
    ax.legend(loc="upper right")
    fig.text(0.5, .015, "Synthetic data • not real fraud performance • does not retrain serving model",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .035, 1, 1))
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-folds", type=int, default=5)
    parser.add_argument("--json", type=Path, default=Path("artifacts/reports/rolling_backtest.json"))
    parser.add_argument("--chart", type=Path, default=Path("artifacts/reports/rolling_backtest.png"))
    args = parser.parse_args()
    report = rolling_origin_report(create_synthetic(n=args.rows, seed=args.seed), max_folds=args.max_folds)
    save_diagnostics(report, args.json, args.chart)
    print(json.dumps({"fold_count": report["fold_count"], "averages": report["averages"],
                      "json": str(args.json), "chart": str(args.chart)}, indent=2))


if __name__ == "__main__":
    main()
