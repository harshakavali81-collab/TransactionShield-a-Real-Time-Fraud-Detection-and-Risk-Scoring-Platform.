import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score, roc_auc_score, confusion_matrix, brier_score_loss

def metrics(y,p,threshold):
    y=np.asarray(y); p=np.asarray(p)
    pred=(p>=threshold).astype(int)
    return {"precision":float(precision_score(y,pred,zero_division=0)),
        "recall":float(recall_score(y,pred,zero_division=0)),
        "f1":float(f1_score(y,pred,zero_division=0)),
        "pr_auc":float(average_precision_score(y,p)),
        "roc_auc":float(roc_auc_score(y,p)) if len(np.unique(y)) == 2 else None,
        "brier_score":float(brier_score_loss(y,p)),
        "confusion_matrix":confusion_matrix(y,pred,labels=[0,1]).tolist(),
        "support":int(len(y)),"positive_cases":int(sum(y)), "threshold":float(threshold)}

def optimize_threshold(y,p):
    """Choose threshold ONLY using a separate validation dataset."""
    from sklearn.metrics import fbeta_score
    candidates=np.linspace(0.03,0.85,83)
    score=[fbeta_score(y,(p>=t).astype(int),beta=2,zero_division=0) for t in candidates]
    return float(candidates[int(np.argmax(score))])
