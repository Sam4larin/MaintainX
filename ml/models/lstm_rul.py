import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from ml.config import ARTIFACTS_DIR


class LSTMRegressor(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 32, num_layers: int = 1):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


def _prepare_sequences(df: pd.DataFrame, sequence_length: int = 30):
    X, y = [], []
    feature_cols = [c for c in df.columns if c not in {'unit_number', 'time_in_cycles', 'rul'}]
    n_features = len(feature_cols)
    for unit in sorted(df['unit_number'].unique()):
        unit_df = df[df['unit_number'] == unit].sort_values('time_in_cycles')
        values = unit_df[feature_cols].to_numpy(dtype=float).reshape(-1, n_features)
        target = unit_df['rul'].to_numpy(dtype=float)
        if len(values) < sequence_length:
            padded = np.zeros((sequence_length, n_features), dtype=float)
            padded[-len(values):] = values
            X.append(padded)
            y.append(target[-1])
        else:
            for end in range(sequence_length, len(values) +1):
                X.append(values[end - sequence_length:end])
                y.append(target[end -1])

    X_arr = np.stack(X).astype(float)
    y_arr = np.array(y, dtype=float)           
    return X_arr, y_arr


def train(train_df: pd.DataFrame, test_df: pd.DataFrame, output_dir: Path | None | str = None, epochs: int = 60, seed: int = 42):
    output_dir = Path(output_dir) if output_dir is not None else ARTIFACTS_DIR / 'regression'
    output_dir.mkdir(parents=True, exist_ok=True)
    # torch.manual_seed alone is NOT sufficient to make LSTM training
    # reproducible (confirmed: identical seed produced different R2 across
    # runs -- 0.78, 0.66, -0.64, -0.25 -- on otherwise-identical code/data).
    # PyTorch's own docs note RNN/LSTM layers can use non-deterministic
    # algorithms regardless of seeding. use_deterministic_algorithms forces
    # deterministic kernels; np.random.seed covers any numpy-side randomness.
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    X_train, y_train = _prepare_sequences(train_df)
    X_test, y_test = _prepare_sequences(test_df)

    X_train = torch.tensor(X_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    y_test = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

    model = LSTMRegressor(input_size=X_train.shape[2])
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_history = []
    batch_size = 256
    n = X_train.shape[0]
    for epoch in range(epochs):
        permutation = torch.randperm(n)
        epoch_loss = 0.0
        for i in range(0, n, batch_size):
            idx = permutation[i:i + batch_size]
            optimizer.zero_grad()
            pred = model(X_train[idx])
            loss = criterion(pred, y_train[idx])
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(idx)
        loss_history.append(epoch_loss / n)

    with torch.no_grad():
        preds = model(X_test).squeeze().numpy()
    y_test_np = y_test.numpy().squeeze()
    metrics = {
        'rmse': root_mean_squared_error(y_test_np, preds),
        'mae': mean_absolute_error(y_test_np, preds),
        'r2': r2_score(y_test_np, preds),
        'final_loss': loss_history[-1],
        'first_loss': loss_history[0],
        'n_train_sequences': int(n),
    }
    torch.save(model.state_dict(), output_dir / 'lstm_rul.pt')
    (output_dir / 'metrics.json').write_text(json.dumps(metrics), encoding='utf-8')
    return model, metrics


def evaluate(model, X_test):
    with torch.no_grad():
        return model(X_test).squeeze().numpy()