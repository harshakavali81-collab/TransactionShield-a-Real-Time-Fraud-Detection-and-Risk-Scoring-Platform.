from pydantic import BaseModel
class PredictionResponse(BaseModel):
    transaction_id:str
    fraud_probability:float
    risk_score:int
    risk_level:str
    is_flagged:bool
    model_version:str
    reasons:list[str]
