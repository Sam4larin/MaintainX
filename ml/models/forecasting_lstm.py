import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import numpy as np
import pandas as pd
import torch
from torch import nn

from ml.config import ARTIFACTS_DIR

SENSOR_COLS = [f'sensor_measurement_{i}' for i in range(1, 22)]


class ForecastingLSTM(nn.Module):
    """Forecasts all present CMAPSS sensor readings `horizon` cycles ahead
    from a `history_length`-cycle window of ALL input features (sensors +
    operational settings). Output width is n_targets * horizon, reshaped
    to (batch, horizon, n_targets) at inference time.
    """
    def __init__(self, input_size: int, n_targets: int, horizon: int = 2):
        super().__init__()
        self.horizon = horizon
        self.n_targets = n_targets
        self.lstm = nn.LSTM(input_size, 32, batch_first=True)
        self.fc = nn.Linear(32, n_targets * horizon)

    def forward(self, x):
        out, _ = self.lstm(x)
        flat = self.fc(out[:, -1, :])
        return flat.view(-1, self.horizon, self.n_targets)


def _prepare_sequences(df: pd.DataFrame, history_length: int = 5, horizon: int = 2):
    X = []
    y = []
    feature_cols = [c for c in df.columns if c not in {'unit_number', 'time_in_cycles', 'rul'}]
    # Use whichever sensor columns are actually present -- upstream feature
    # building (cmapss_features.py) drops low-variance sensors, so the full
    # 21-sensor list may not all exist in `df`.
    sensor_cols = [c for c in SENSOR_COLS if c in feature_cols]
    target_idx = [feature_cols.index(c) for c in sensor_cols]
    for unit in sorted(df['unit_number'].unique()):
        unit_df = df[df['unit_number'] == unit].sort_values('time_in_cycles')
        features = unit_df[feature_cols].to_numpy(dtype=float)
        for i in range(len(features) - history_length - horizon + 1):
            X.append(features[i:i + history_length])
            # y shape per sample: (horizon, n_sensors) -- ALL present sensors,
            # not just column 0 (which previously silently meant
            # operational_setting_1, not a real sensor reading)
            y.append(features[i + history_length:i + history_length + horizon][:, target_idx])
    return np.array(X, dtype=float), np.array(y, dtype=float), feature_cols, sensor_cols


def train(train_df: pd.DataFrame, output_dir: Path | None | str = None, history_length: int = 5, horizon: int = 2, seed: int = 42):
    output_dir = Path(output_dir) if output_dir is not None else ARTIFACTS_DIR / 'forecasting'
    output_dir.mkdir(parents=True, exist_ok=True)
    # Reproducibility fix (same root cause found for lstm_rul.py this
    # session: plain torch.manual_seed() alone was verified insufficient
    # for LSTM determinism; use_deterministic_algorithms closes the gap).
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)

    X, y, feature_cols, sensor_cols = _prepare_sequences(train_df, history_length=history_length, horizon=horizon)
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)
    model = ForecastingLSTM(input_size=X.shape[2], n_targets=len(sensor_cols), horizon=horizon)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_history = []
    for _ in range(30):
        optimizer.zero_grad()
        pred = model(X_tensor)
        loss = criterion(pred, y_tensor)
        loss.backward()
        optimizer.step()
        loss_history.append(float(loss.item()))

    torch.save(model.state_dict(), output_dir / 'forecasting_lstm.pt')
    (output_dir / 'model_config.json').write_text(
        json.dumps({
            'input_size': X.shape[2], 'n_targets': len(sensor_cols), 'horizon': horizon,
            'history_length': history_length, 'feature_cols': feature_cols, 'sensor_cols': sensor_cols,
        }), encoding='utf-8')
    (output_dir / 'metrics.json').write_text(
        json.dumps({'samples': len(X), 'final_loss': loss_history[-1], 'first_loss': loss_history[0]}),
        encoding='utf-8')
    return model


def evaluate(model, X):
    with torch.no_grad():
        return model(X).numpy()


def evaluate_metrics(model, X_test, y_test, sensor_cols):
    model.eval()
    if isinstance(X_test, np.ndarray):
        X_tensor = torch.tensor(X_test, dtype=torch.float32)
    else:
        X_tensor = X_test

    if isinstance(y_test, torch.Tensor):
        y_test_np = y_test.numpy()
    else:
        y_test_np = np.array(y_test, dtype=float)

    with torch.no_grad():
        preds = model(X_tensor).numpy()

    per_sensor = {}
    rmse_list = []
    mae_list = []

    for i, s_col in enumerate(sensor_cols):
        y_true_s = y_test_np[:, :, i].flatten()
        y_pred_s = preds[:, :, i].flatten()
        rmse = float(np.sqrt(np.mean((y_pred_s - y_true_s) ** 2)))
        mae = float(np.mean(np.abs(y_pred_s - y_true_s)))
        per_sensor[s_col] = {"rmse": rmse, "mae": mae}
        rmse_list.append(rmse)
        mae_list.append(mae)

    overall = {
        "rmse": float(np.mean(rmse_list)),
        "mae": float(np.mean(mae_list)),
    }

    return {
        "per_sensor": per_sensor,
        "overall": overall,
    }