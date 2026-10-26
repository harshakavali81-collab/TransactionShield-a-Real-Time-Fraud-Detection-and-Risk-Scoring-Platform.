from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
class TransactionIn(BaseModel):
    model_config=ConfigDict(extra="forbid")
    amount:float=Field(ge=0,le=1000000)
    hour:int=Field(ge=0,le=23)
    account_age_days:int=Field(ge=0,le=100000)
    velocity_24h:int=Field(ge=0,le=10000)
    prior_chargebacks:int=Field(ge=0,le=100)
    ip_risk_score:float=Field(ge=0,le=1)
    is_international:int=Field(ge=0,le=1)
    is_new_device:int=Field(ge=0,le=1)
    merchant_category:str=Field(min_length=1,max_length=64)
    transaction_type:str=Field(min_length=1,max_length=64)
    transaction_id:str|None=Field(default=None,min_length=1,max_length=80,pattern=r"^[A-Za-z0-9_-]+$")
class TransactionOut(BaseModel):
    transaction_id:str
    created_at:datetime
    fraud_probability:float
    risk_score:int
    risk_level:str
    is_flagged:bool
    model_version:str
    reasons:list[str]
