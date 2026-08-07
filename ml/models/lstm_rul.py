import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ml.config import ARTIFACTS_DIR


class LSTMRegressor(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 16, num_layers: int = 1):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


def _prepare_sequences(df: pd.DataFrame, sequence_length: int = 30):
    X = []
    y = []
    for unit in sorted(df['unit_number'].unique()):
        unit_df = df[df['unit_number'] == unit].copy()
        values = unit_df.drop(columns=['unit_number', 'time_in_cycles', 'rul']).to_numpy(dtype=float)
        target = unit_df['rul'].to_numpy(dtype=float)
        if len(values) < sequence_length:
            padded = np.zeros((sequence_length, values.shape[1]), dtype=float)
            padded[-len(values):] = values
            values = padded
            target_seq = np.zeros(sequence_length, dtype=float)
            target_seq[-len(target):] = target
        else:
            values = values[-sequence_length:]
            target_seq = target[-sequence_length:]
        X.append(values)
        y.append(target_seq[-1])
    return np.array(X, dtype=float), np.array(y, dtype=float)


def train(train_df: pd.DataFrame, test_df: pd.DataFrame, output_dir: Path | None | str = None):
    output_dir = Path(output_dir) if output_dir is not None else ARTIFACTS_DIR / 'regression'
    output_dir.mkdir(parents=True, exist_ok=True)
    X_train, y_train = _prepare_sequences(train_df)
    X_test, y_test = _prepare_sequences(test_df)

    X_train = torch.tensor(X_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    y_test = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

    model = LSTMRegressor(input_size=X_train.shape[2])
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    for _ in range(5):
        optimizer.zero_grad()
        pred = model(X_train)
        loss = criterion(pred, y_train)
        loss.backward()
        optimizer.step()

    with torch.no_grad():
        preds = model(X_test).squeeze().numpy()
    metrics = {
        'rmse': mean_squared_error(y_test.numpy().squeeze(), preds, squared=False),
        'mae': mean_absolute_error(y_test.numpy().squeeze(), preds),
        'r2': r2_score(y_test.numpy().squeeze(), preds),
    }
    torch.save(model.state_dict(), output_dir / 'lstm_rul.pt')
    (output_dir / 'metrics.json').write_text(json.dumps(metrics), encoding='utf-8')
    return model, metrics


def evaluate(model, X_test):
    return model(X_test)
