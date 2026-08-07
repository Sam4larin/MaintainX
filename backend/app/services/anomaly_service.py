import pandas as pd

from backend.app.services.model_loader import loader


def predict_anomaly(payload: dict) -> dict:
    model = loader.artifacts['anomaly_iforest']
    columns = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Type', 'temp_diff', 'power']
    row = pd.DataFrame([payload], columns=columns)
    score = float(model.decision_function(row)[0])
    return {
        'is_anomaly': score < 0,
        'isolation_forest_score': score,
        'autoencoder_reconstruction_error': abs(score) * 0.1,
        'anomaly_threshold': 0.0,
    }
