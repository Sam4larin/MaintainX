import numpy as np
import pandas as pd

from backend.app.services.model_loader import loader


def _ai4i_row(payload: dict) -> pd.DataFrame:
    raw = {
        'Air_temperature': payload['Air_temperature_K'],
        'Process_temperature': payload['Process_temperature_K'],
        'Rotational_speed': payload['Rotational_speed_rpm'],
        'Torque': payload['Torque_Nm'],
        'Tool_wear': payload['Tool_wear_min'],
        'Type': payload['Type'],
        'temp_diff': payload['temp_diff'],
        'power': payload['power'],
    }
    feature_order = list(loader.artifacts['ai4i_scaler'].feature_names_in_)
    row = pd.DataFrame([raw], columns=feature_order)
    scaled = row.copy()
    scaled[row.columns] = loader.artifacts['ai4i_scaler'].transform(row)
    return scaled


def predict_failure_risk(payload: dict) -> dict:
    loader.ensure_loaded()
    model = loader.artifacts['classification_binary']
    multi_model = loader.artifacts['classification_multiclass']
    labels = loader.artifacts['classification_labels']
    row = _ai4i_row(payload)
    probs = model.predict_proba(row)[0]
    prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
    risk = 'Critical' if prob > 0.7 else 'High' if prob > 0.4 else 'Medium' if prob > 0.2 else 'Low'
    failure_type_index = int(multi_model.predict(row)[0])
    failure_type_pred = str(labels[failure_type_index])
    failure_type_probabilities = {str(labels[int(label)]): float(prob) for label, prob in zip(multi_model.classes_, multi_model.predict_proba(row)[0])}
    return {
        'failure_probability': prob,
        'risk_level': risk,
        'failure_type_prediction': str(failure_type_pred),
        'failure_type_probabilities': failure_type_probabilities,
    }
