import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from ml.data.load_data import load_data
from ml.config import REPORTS

def main():
 df=load_data();REPORTS.mkdir(parents=True,exist_ok=True)
 report={"records":len(df),"fraud_rate":float(df.is_fraud.mean()),"median_amount":float(df.amount.median()),"by_category":df.groupby('merchant_category').is_fraud.agg(['mean','count']).round(4).to_dict(orient='index')}
 (REPORTS/"eda_summary.json").write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
