import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

from ml.config import ARTIFACTS_DIR


class ForecastingLSTM(nn.Module):
    def __init__(self, input_size: int):
        super().__init__()
        self.lstm = nn.LSTM(input_size, 8, batch_first=True)
        self.fc = nn.Linear(8, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


def _prepare_sequences(df: pd.DataFrame, history_length: int = 5, horizon: int = 2):
    X = []
    y = []
    for unit in sorted(df['unit_number'].unique()):
        unit_df = df[df['unit_number'] == unit].copy()
        features = unit_df.drop(columns=['unit_number', 'time_in_cycles']).to_numpy(dtype=float)
        for i in range(len(features) - history_length - horizon + 1):
            X.append(features[i:i + history_length])
            y.append(features[i + history_length:i + history_length + horizon, 0])
    return np.array(X, dtype=float), np.array(y, dtype=float)


def train(train_df: pd.DataFrame, output_dir: Path | None | str = None):
    output_dir = Path(output_dir) if output_dir is not None else ARTIFACTS_DIR / 'forecasting'
    output_dir.mkdir(parents=True, exist_ok=True)
    X, y = _prepare_sequences(train_df)
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)
    model = ForecastingLSTM(input_size=X.shape[2])
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    for _ in range(5):
        optimizer.zero_grad()
        pred = model(X_tensor)
        loss = criterion(pred, y_tensor)
        loss.backward()
        optimizer.step()
    torch.save(model.state_dict(), output_dir / 'forecasting_lstm.pt')
    (output_dir / 'metrics.json').write_text(json.dumps({'samples': len(X)}), encoding='utf-8')
    return model


def evaluate(model, X):
    with torch.no_grad():
        return model(X).numpy()
