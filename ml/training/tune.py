"""Hyperparameter tuning belongs to training/validation only, never the held-out test."""
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from ml.data.feature_engineering import make_preprocessor

def time_series_search(X,y):
    pipeline=Pipeline([("preprocess",make_preprocessor()),("model",RandomForestClassifier(class_weight="balanced_subsample",random_state=42,n_jobs=2))])
    search=RandomizedSearchCV(pipeline,{"model__max_depth":[4,7,10],"model__min_samples_leaf":[2,5,10]},n_iter=5,cv=TimeSeriesSplit(n_splits=3),scoring="average_precision",random_state=42,n_jobs=1)
    return search.fit(X,y)
