import torch

from backend.app.services.classification_service import _ai4i_row
from backend.app.services.model_loader import loader
from ml.models.anomaly_autoencoder import Autoencoder


def predict_anomaly(payload: dict) -> dict:
    loader.ensure_loaded()
    model = loader.artifacts['anomaly_iforest']
    row = _ai4i_row(payload)
    score = float(model.decision_function(row)[0])

    autoencoder = Autoencoder(input_dim=row.shape[1])
    autoencoder.load_state_dict(loader.artifacts['anomaly_autoencoder_state'])
    autoencoder.eval()
    X_tensor = torch.tensor(row.to_numpy(dtype=float), dtype=torch.float32)
    with torch.no_grad():
        reconstruction_error = float(((autoencoder(X_tensor) - X_tensor) ** 2).mean().item())

    threshold = loader.artifacts['anomaly_threshold']
    return {
        'is_anomaly': bool(score < 0 or reconstruction_error > threshold),
        'isolation_forest_score': score,
        'autoencoder_reconstruction_error': reconstruction_error,
        'anomaly_threshold': threshold,
    }