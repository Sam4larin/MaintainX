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
        required_files = {
            'classification_binary': ARTIFACTS_DIR / 'classification' / 'binary_classifier.joblib',
            'classification_multiclass': ARTIFACTS_DIR / 'classification' / 'multiclass_classifier.joblib',
            'classification_labels': ARTIFACTS_DIR / 'classification' / 'multiclass_labels.joblib',
            'ai4i_scaler': ARTIFACTS_DIR / 'classification' / 'ai4i_scaler.joblib',
            'regression_xgboost': ARTIFACTS_DIR / 'regression' / 'xgboost_rul.joblib',
            'regression_lstm_state': ARTIFACTS_DIR / 'regression' / 'lstm_rul.pt',
            'cmapss_scaler': ARTIFACTS_DIR / 'regression' / 'cmapss_scaler.joblib',
            'anomaly_iforest': ARTIFACTS_DIR / 'anomaly' / 'isolation_forest.joblib',
            'anomaly_autoencoder_state': ARTIFACTS_DIR / 'anomaly' / 'autoencoder.pt',
            'anomaly_threshold_file': ARTIFACTS_DIR / 'anomaly' / 'threshold.json',
            'forecasting_lstm_state': ARTIFACTS_DIR / 'forecasting' / 'forecasting_lstm.pt',
            'forecasting_config': ARTIFACTS_DIR / 'forecasting' / 'model_config.json',
        }
        missing = [str(path) for path in required_files.values() if not path.exists()]
        if missing:
            raise FileNotFoundError(
                'Expected artifact files are missing. Run python -m ml.pipeline.train_all first. '
                f'Missing: {missing}'
            )

        joblib_keys = {'classification_binary', 'classification_multiclass', 'classification_labels',
                       'ai4i_scaler', 'regression_xgboost', 'cmapss_scaler', 'anomaly_iforest'}
        torch_keys = {'regression_lstm_state', 'anomaly_autoencoder_state', 'forecasting_lstm_state'}

        for key, path in required_files.items():
            if key in joblib_keys:
                self.artifacts[key] = joblib.load(path)
            elif key in torch_keys:
                self.artifacts[key] = torch.load(path, map_location='cpu')
            elif key == 'forecasting_config':
                self.artifacts[key] = json.loads(path.read_text(encoding='utf-8'))
            elif key == 'anomaly_threshold_file':
                self.artifacts['anomaly_threshold'] = json.loads(path.read_text(encoding='utf-8'))['threshold']

        self.artifacts['summary'] = json.loads((ARTIFACTS_DIR / 'summary.json').read_text(encoding='utf-8')) if (ARTIFACTS_DIR / 'summary.json').exists() else {}

    def ensure_loaded(self):
        if not self.artifacts:
            self.load()


loader = ModelLoader()