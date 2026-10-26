"""Optional REST client simulator. Polling UI is not streaming event infrastructure."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse,random,time
from ml.data.generate import create_synthetic
import requests

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--count",type=int,default=25);parser.add_argument("--interval",type=float,default=1);parser.add_argument("--url",default="http://localhost:8000")
    args=parser.parse_args();df=create_synthetic(max(args.count,20),seed=random.randint(1,100000))
    from ml.config import FEATURES
    for _,r in df.head(args.count).iterrows():
        req=r[FEATURES].to_dict()
        for col in ["hour","account_age_days","velocity_24h","prior_chargebacks","is_international","is_new_device"]:req[col]=int(req[col])
        res=requests.post(args.url+"/predict",json=req,timeout=10); print(res.status_code,res.text[:300]);time.sleep(args.interval)
if __name__=="__main__":main()
