"""Live precision/recall requires independently confirmed delayed fraud labels."""
from sklearn.metrics import precision_score,recall_score

def confirmed_label_metrics(y_true,y_pred):
    return {"precision":float(precision_score(y_true,y_pred,zero_division=0)),"recall":float(recall_score(y_true,y_pred,zero_division=0)),"count":len(y_true)}
