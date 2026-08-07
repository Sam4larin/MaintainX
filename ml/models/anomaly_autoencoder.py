import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

from ml.config import ARTIFACTS_DIR


class Autoencoder(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(input_dim, 8), nn.ReLU())
        self.decoder = nn.Sequential(nn.Linear(8, input_dim))

    def forward(self, x):
        encoded = self.encoder(x)
        return self.decoder(encoded)


def train(df: pd.DataFrame, output_dir: Path | None | str = None):
    output_dir = Path(output_dir) if output_dir is not None else ARTIFACTS_DIR / 'anomaly'
    output_dir.mkdir(parents=True, exist_ok=True)
    normal = df[df['Machine failure'] == 0].copy()
    features = [c for c in normal.columns if c not in {'Machine failure', 'failure_type'}]
    X = torch.tensor(normal[features].to_numpy(dtype=float), dtype=torch.float32)
    model = Autoencoder(input_dim=X.shape[1])
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    for _ in range(10):
        optimizer.zero_grad()
        recon = model(X)
        loss = criterion(recon, X)
        loss.backward()
        optimizer.step()
    with torch.no_grad():
        errors = ((model(X) - X) ** 2).mean(dim=1).numpy()
    threshold = float(np.quantile(errors, 0.95))
    torch.save(model.state_dict(), output_dir / 'autoencoder.pt')
    (output_dir / 'threshold.json').write_text(json.dumps({'threshold': threshold}), encoding='utf-8')
    return model, threshold


def evaluate(model, X: pd.DataFrame):
    X_tensor = torch.tensor(X.to_numpy(dtype=float), dtype=torch.float32)
    with torch.no_grad():
        return ((model(X_tensor) - X_tensor) ** 2).mean(dim=1).numpy()
