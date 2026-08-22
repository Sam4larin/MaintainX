import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.metrics import precision_score, recall_score, f1_score
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from ml.config import ARTIFACTS_DIR


class Autoencoder(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(input_dim, 8), nn.ReLU())
        self.decoder = nn.Sequential(nn.Linear(8, input_dim))

    def forward(self, x):
        encoded = self.encoder(x)
        return self.decoder(encoded)


def train(df: pd.DataFrame, output_dir: Path | None | str = None, epochs: int = 200, seed: int = 42):
    output_dir = Path(output_dir) if output_dir is not None else ARTIFACTS_DIR / 'anomaly'
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(seed)
    normal = df[df['Machine_failure'] == 0].copy()
    features = [c for c in normal.columns if c not in {'Machine_failure', 'failure_type'}]
    X = torch.tensor(normal[features].to_numpy(dtype=float), dtype=torch.float32)
    model = Autoencoder(input_dim=X.shape[1])
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_history = []
    for epoch in range(epochs):
        optimizer.zero_grad()
        recon = model(X)
        loss = criterion(recon, X)
        loss.backward()
        optimizer.step()
        loss_history.append(float(loss.item()))
    with torch.no_grad():
        errors = ((model(X) - X) ** 2).mean(dim=1).numpy()
    threshold = float(np.quantile(errors, 0.95))

    X_full = torch.tensor(df[features].to_numpy(dtype=float), dtype=torch.float32)
    with torch.no_grad():
        full_errors = ((model(X_full) - X_full) ** 2).mean(dim=1).numpy()
    anomaly_flags = (full_errors > threshold).astype(int)
    labels = (df['Machine_failure'] == 1).astype(int)
    metrics = {
        'precision': precision_score(labels, anomaly_flags, zero_division=0),
        'recall': recall_score(labels, anomaly_flags, zero_division=0),
        'f1': f1_score(labels, anomaly_flags, zero_division=0),
        'final_loss': loss_history[-1],
        'first_loss': loss_history[0],
    }

    torch.save(model.state_dict(), output_dir / 'autoencoder.pt')
    (output_dir / 'threshold.json').write_text(json.dumps({'threshold': threshold}), encoding='utf-8')
    (output_dir / 'metrics.json').write_text(json.dumps(metrics), encoding='utf-8')
    return model, threshold, metrics


def evaluate(model, X: pd.DataFrame, threshold: float):
    X_tensor = torch.tensor(X.to_numpy(dtype=float), dtype=torch.float32)
    with torch.no_grad():
        errors = ((model(X_tensor) - X_tensor) ** 2).mean(dim=1).numpy()
    return (errors > threshold) .astype(int), errors