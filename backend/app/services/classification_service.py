import numpy as np
import pandas as pd

from backend.app.services.model_loader import loader


def predict_failure_risk(payload: dict) -> dict:
    model = loader.artifacts['classification_binary']
    multi_model = loader.artifacts['classification_multiclass']
    columns = [
        'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]',
        'Type', 'temp_diff', 'power'
    ]
    row = pd.DataFrame([payload], columns=columns)
    probs = model.predict_proba(row)[0]
    prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
    risk = 'Critical' if prob > 0.7 else 'High' if prob > 0.4 else 'Medium' if prob > 0.2 else 'Low'
    failure_type_pred = multi_model.predict(row)[0]
    failure_type_probabilities = {label: float(prob) for label, prob in zip(multi_model.classes_, multi_model.predict_proba(row)[0])}
    return {
        'failure_probability': prob,
        'risk_level': risk,
        'failure_type_prediction': str(failure_type_pred),
        'failure_type_probabilities': failure_type_probabilities,
    }
