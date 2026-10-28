"""Time-ordered training, model comparison, threshold tuning, held-out evaluation."""
import argparse, json, os
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score
from sklearn.utils.class_weight import compute_sample_weight
from ml.config import DATA, MODEL, METRICS, NUMERIC, FEATURES
from ml.data.generate import create_synthetic
from ml.data.load_data import load_data
from ml.data.feature_engineering import make_preprocessor
from ml.training.evaluate import metrics,optimize_threshold
from ml.training.save_model import save_model
from ml.training.model_integrity import write_manifest

def candidates(seed=42,fast=False):
    models={"logistic_regression":LogisticRegression(max_iter=600, class_weight="balanced", random_state=seed),
        "random_forest":RandomForestClassifier(n_estimators=55 if fast else 120, max_depth=10, min_samples_leaf=5, n_jobs=-1, class_weight="balanced_subsample",random_state=seed)}
    try:
        from xgboost import XGBClassifier
        models["xgboost"]=XGBClassifier(n_estimators=65 if fast else 130,max_depth=3,learning_rate=.065,subsample=.85,colsample_bytree=.9,eval_metric="logloss",n_jobs=2,random_state=seed)
    except ImportError: pass
    try:
        from lightgbm import LGBMClassifier
        models["lightgbm"]=LGBMClassifier(n_estimators=65 if fast else 130,max_depth=5,learning_rate=.05,num_leaves=12,verbosity=-1,random_state=seed,n_jobs=2)
    except ImportError:pass
    return models

def train(data_path=DATA,fast=False,tracking=False):
    if not data_path.exists():
        data_path.parent.mkdir(parents=True,exist_ok=True)
        create_synthetic(n=2000 if fast else 4000).to_csv(data_path,index=False)
    df=load_data(data_path)
    if len(df)<250:raise ValueError("Need >=250 rows")
    n=len(df); i=int(n*.6);j=int(n*.8)
    train_df,val_df,test_df=df.iloc[:i],df.iloc[i:j],df.iloc[j:]
    y_train=train_df.is_fraud; y_val=val_df.is_fraud; y_test=test_df.is_fraud
    if any(y.nunique()<2 for y in [y_train,y_val,y_test]): raise ValueError("Each chronological split must contain both classes; collect more labeled data")
    leaderboard=[]; fitted=[]
    for name,est in candidates(fast=fast).items():
        model=Pipeline([("preprocess",make_preprocessor()), ("model",est)])
        model.fit(train_df[FEATURES],y_train)
        vp=model.predict_proba(val_df[FEATURES])[:,1]
        ap=float(average_precision_score(y_val,vp))
        leaderboard.append({"name":name,"validation_pr_auc":round(ap,6)})
        fitted.append((name,model,vp,ap))
    name,best,validation_pred,_=max(fitted,key=lambda r:r[3])
    threshold=optimize_threshold(y_val,validation_pred)
    test_prob=best.predict_proba(test_df[FEATURES])[:,1]
    report={"dataset":"synthetic demonstration data", "rows":n,"fraud_rate":float(df.is_fraud.mean()),
        "chronological_split":{"train":len(train_df),"validation":len(val_df),"test":len(test_df)},
        "selected_model":name,"threshold_source":"validation F2 maximum", "model_comparison":leaderboard,
        "test":metrics(y_test,test_prob,threshold),"test_only_evaluated_once":True}
    reference={col:{"mean":float(train_df[col].mean()),"std":float(train_df[col].std() or 1)} for col in NUMERIC}
    save_model({"pipeline":best,"threshold":threshold,"model_name":name,"reference_stats":reference,"features":FEATURES})
    METRICS.parent.mkdir(parents=True,exist_ok=True)
    METRICS.write_text(json.dumps(report,indent=2))
    write_manifest(MODEL, METRICS, report)
    if tracking or os.environ.get("ENABLE_MLFLOW") == "1":
        try:
            import mlflow
            mlflow.set_experiment("TransactionShield-Synthetic")
            with mlflow.start_run(run_name=name):
                mlflow.log_param("data","synthetic")
                mlflow.log_param("selected_model",name)
                mlflow.log_metric("test_pr_auc",report["test"]["pr_auc"])
                mlflow.log_metric("test_recall",report["test"]["recall"])
                mlflow.log_metric("threshold",threshold)
                mlflow.log_artifact(str(METRICS))
        except ImportError as ex: raise RuntimeError("Install mlflow or omit --tracking") from ex
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--fast",action="store_true");parser.add_argument("--tracking",action="store_true")
    args=parser.parse_args()
    print(json.dumps(train(fast=args.fast,tracking=args.tracking),indent=2))
