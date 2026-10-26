import numpy as np
from ml.training.evaluate import metrics,optimize_threshold
from ml.training.train import candidates

def test_score_report():
    y=[0,1,0,1,0,0];p=[.1,.85,.2,.61,.4,.05]
    report=metrics(y,p,.5)
    assert report['recall']==1.0
    assert report['precision']==1.0
    assert report['confusion_matrix']==[[4,0],[0,2]]

def test_validation_threshold_range():
    t=optimize_threshold([0,1,0,1],[.1,.8,.2,.9])
    assert .03<=t<=.85

def test_candidate_baselines_present():
    c=candidates(fast=True)
    assert 'logistic_regression' in c and 'random_forest' in c
