import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import PrecisionRecallDisplay, ConfusionMatrixDisplay
from ml.config import DATA, MODEL, METRICS, REPORTS, FEATURES
from ml.training.save_model import load_model
from ml.data.load_data import load_data
from sklearn.metrics import precision_recall_curve

def create_charts():
    if not MODEL.exists() or not DATA.exists():raise RuntimeError("Run training and synthetic data generation first")
    REPORTS.mkdir(parents=True,exist_ok=True)
    df=load_data(); payload=load_model(); m=json.loads(METRICS.read_text())
    test=df.iloc[int(len(df)*.8):]
    p=payload["pipeline"].predict_proba(test[FEATURES])[:,1]
    fig,ax=plt.subplots(figsize=(7,4));ax.hist([test.loc[test.is_fraud==0,"amount"].clip(upper=2000),test.loc[test.is_fraud==1,"amount"].clip(upper=2000)],bins=30,label=["Non-fraud (synthetic)","Fraud (synthetic)"],alpha=.7);ax.set(title="Amounts by simulated class",xlabel="Transaction amount (capped at 2000)",ylabel="Observations");ax.legend();fig.tight_layout();fig.savefig(REPORTS/"synthetic_amounts.png",dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4));PrecisionRecallDisplay.from_predictions(test.is_fraud,p,ax=ax);ax.set_title("Held-out synthetic precision-recall curve");fig.tight_layout();fig.savefig(REPORTS/"precision_recall.png",dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(5,4));ConfusionMatrixDisplay.from_predictions(test.is_fraud,p>=payload["threshold"],ax=ax,colorbar=False);ax.set_title("Synthetic held-out confusion matrix");fig.tight_layout();fig.savefig(REPORTS/"confusion_matrix.png",dpi=140);plt.close(fig)
    labels=[r["name"] for r in m["model_comparison"]];vals=[r["validation_pr_auc"] for r in m["model_comparison"]]
    fig,ax=plt.subplots(figsize=(8,4));ax.barh(labels,vals);ax.set(xlabel="Validation PR-AUC",title="Model comparison on synthetic validation split",xlim=(0,max(.1,max(vals)*1.15)));fig.tight_layout();fig.savefig(REPORTS/"model_comparison.png",dpi=140);plt.close(fig)
    print("Saved charts:",list(map(str,REPORTS.glob("*.png"))))
if __name__=="__main__":create_charts()
