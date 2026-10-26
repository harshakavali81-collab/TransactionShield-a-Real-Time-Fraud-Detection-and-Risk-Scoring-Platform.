import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.config import DATA
from ml.data.generate import create_synthetic

def main():
    DATA.parent.mkdir(parents=True, exist_ok=True)
    df=create_synthetic()
    df.to_csv(DATA,index=False)
    print(f"Saved {len(df)} synthetic rows to {DATA}; generated fraud rate: {df.is_fraud.mean():.2%}")
if __name__=="__main__":main()
