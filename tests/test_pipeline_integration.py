from ml.config import FEATURES
from ml.data.generate import create_synthetic
from ml.data.feature_engineering import make_preprocessor
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

def test_trained_pipeline_predicts_probabilities():
    df=create_synthetic(350)
    model=Pipeline([('preprocess',make_preprocessor()),('model',LogisticRegression(max_iter=600,class_weight='balanced'))])
    model.fit(df[FEATURES].iloc[:250],df.is_fraud.iloc[:250])
    p=model.predict_proba(df[FEATURES].iloc[250:])
    assert p.shape==(100,2)
    assert ((p>=0)&(p<=1)).all()
