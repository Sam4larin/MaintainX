import json
import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import torch

from backend.app.config import settings

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = Path(settings.artifacts_path) if settings.artifacts_path.startswith('/') else ROOT / settings.artifacts_path


class ModelLoader:
    def __init__(self):
        self.artifacts: dict[str, Any] = {}

    def load(self):
        required_files = [
            ARTIFACTS_DIR / 'classification' / 'binary_classifier.joblib',
            ARTIFACTS_DIR / 'classification' / 'multiclass_classifier.joblib',
            ARTIFACTS_DIR / 'regression' / 'xgboost_rul.joblib',
            ARTIFACTS_DIR / 'regression' / 'lstm_rul.pt',
            ARTIFACTS_DIR / 'anomaly' / 'isolation_forest.joblib',
            ARTIFACTS_DIR / 'anomaly' / 'autoencoder.pt',
            ARTIFACTS_DIR / 'forecasting' / 'forecasting_lstm.pt',
        ]
        missing = [str(path) for path in required_files if not path.exists()]
        if missing:
            raise FileNotFoundError('Expected artifact files are missing. Run python -m ml.pipeline.train_all first.')

        self.artifacts['classification_binary'] = joblib.load(required_files[0])
        self.artifacts['classification_multiclass'] = joblib.load(required_files[1])
        self.artifacts['regression_xgboost'] = joblib.load(required_files[2])
        self.artifacts['regression_lstm_state'] = torch.load(required_files[3], map_location='cpu')
        self.artifacts['anomaly_iforest'] = joblib.load(required_files[4])
        self.artifacts['anomaly_autoencoder_state'] = torch.load(required_files[5], map_location='cpu')
        self.artifacts['forecasting_lstm_state'] = torch.load(required_files[6], map_location='cpu')
        self.artifacts['summary'] = json.loads((ARTIFACTS_DIR / 'summary.json').read_text(encoding='utf-8')) if (ARTIFACTS_DIR / 'summary.json').exists() else {}


loader = ModelLoader()
