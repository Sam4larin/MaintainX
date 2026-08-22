import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from ml.config import ARTIFACTS_DIR


def train(df: pd.DataFrame, output_dir: Path | None | str = None):
    output_dir = Path(output_dir) if output_dir is not None else ARTIFACTS_DIR / 'anomaly'
    output_dir.mkdir(parents=True, exist_ok=True)
    normal = df[df['Machine_failure'] == 0].copy()
    features = [c for c in normal.columns if c not in {'Machine_failure', 'failure_type'}]
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(normal[features])
    scores = model.decision_function(df[features])
    preds = model.predict(df[features])
    anomaly_flags = (preds == -1).astype(int)
    labels = (df['Machine_failure'] == 1).astype(int)
    metrics = {
        'precision': precision_score(labels, anomaly_flags, zero_division=0),
        'recall': recall_score(labels, anomaly_flags, zero_division=0),
        'f1': f1_score(labels, anomaly_flags, zero_division=0),
    }
    joblib.dump(model, output_dir / 'isolation_forest.joblib')
    (output_dir / 'metrics.json').write_text(json.dumps(metrics), encoding='utf-8')
    return model, metrics


def evaluate(model, X: pd.DataFrame):
    return model.decision_function(X)
