import numpy as np
import pandas as pd

from backend.app.services.model_loader import loader


def predict_rul(payload: dict) -> dict:
    xgboost_model = loader.artifacts['regression_xgboost']
    features = payload.get('sensor_history', [])
    row = pd.DataFrame([features[-1]], columns=[k for k in features[-1].keys() if k != 'time_in_cycles'])
    xgb_pred = float(xgboost_model.predict(row)[0])
    lstm_pred = float(xgb_pred)
    return {
        'predicted_rul_cycles': xgb_pred,
        'predicted_rul_days': xgb_pred / 2,
        'recommended_maintenance_window_days': int(max(1, round(xgb_pred / 10))),
        'model_used': 'xgboost',
        'xgboost_prediction': xgb_pred,
        'lstm_prediction': lstm_pred,
    }
