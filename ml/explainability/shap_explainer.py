"""Optional SHAP plot for compatible tree models; export is a model explanation, not a causal claim."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from ml.training.save_model import load_model

def export_shap(df, output="artifacts/reports/shap_summary.png", max_samples=100):
    import shap
    payload=load_model();pipeline=payload["pipeline"]
    estimator=pipeline.named_steps["model"]
    preprocessor=pipeline.named_steps["preprocess"]
    if payload["model_name"] not in {"random_forest", "xgboost", "lightgbm"}:
        raise ValueError("Selected model is not tree-based; use permutation importance instead")
    X=preprocessor.transform(df[payload["features"]].head(max_samples))
    explainer=shap.TreeExplainer(estimator)
    values=explainer.shap_values(X)
    if isinstance(values,list): values=values[-1]
    if np.asarray(values).ndim==3: values=np.asarray(values)[:,:,1]
    labels=preprocessor.get_feature_names_out()
    shap.summary_plot(values,X,feature_names=labels,show=False,max_display=12)
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    plt.tight_layout();plt.savefig(output,dpi=160,bbox_inches="tight");plt.close()
    return str(output)
