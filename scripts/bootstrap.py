"""Create synthetic data, train and generate portfolio charts locally."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.generate_demo import main as generate
from ml.training.train import train
from scripts.create_report import create_charts
if __name__=="__main__":
    generate()
    print(train())
    create_charts()
