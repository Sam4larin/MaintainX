import numpy as np
import pandas as pd
import torch

from backend.app.services.model_loader import loader
from ml.models.lstm_rul import LSTMRegressor

SENSOR_COLS = [f'sensor_measurement_{i}' for i in range(1, 22)]
LSTM_SEQUENCE_LENGTH = 30
# Matches ml/models/lstm_rul.py train(): targets were scaled to [0, 1] by
# dividing by this cap before training, so raw model output must be
# multiplied back by the same constant to recover real RUL cycles.
LSTM_RUL_CAP = 125.0


def _build_engineered_features(history: list[dict]) -> pd.DataFrame:
    """Reconstruct the same engineered features used at training time
    (ml/features/cmapss_features.py: add_rolling_features) for EVERY cycle
    in the given history, in order. Returns one row per input cycle -- the
    XGBoost path uses only the last row; the LSTM path uses the trailing
    window of up to LSTM_SEQUENCE_LENGTH rows as its sequence input.
    """
    if not history:
        raise ValueError('sensor_history must contain at least one reading')

    df = pd.DataFrame(history).sort_values('time_in_cycles').reset_index(drop=True)
    missing_sensors = [c for c in SENSOR_COLS if c not in df.columns]
    if missing_sensors:
        raise ValueError(f'sensor_history rows are missing required sensor columns: {missing_sensors}')

    df['unit_number'] = 0
    grouped_frames = {}
    for sensor in SENSOR_COLS:
        g = df.groupby('unit_number')[sensor]
        grouped_frames[f'{sensor}_roll5_mean'] = g.transform(lambda s: s.rolling(5, min_periods=1).mean())
        grouped_frames[f'{sensor}_roll5_std'] = g.transform(lambda s: s.rolling(5, min_periods=1).std().fillna(0))
        grouped_frames[f'{sensor}_roll20_mean'] = g.transform(lambda s: s.rolling(20, min_periods=1).mean())
        grouped_frames[f'{sensor}_roll20_std'] = g.transform(lambda s: s.rolling(20, min_periods=1).std().fillna(0))
        baseline = g.transform(lambda s: s.iloc[:5].mean())
        grouped_frames[f'{sensor}_baseline_diff'] = df[sensor] - baseline
        grouped_frames[f'{sensor}_trend20'] = g.transform(lambda s: s.rolling(20, min_periods=1).apply(lambda w: w.iloc[-1] - w.iloc[0], raw=False).fillna(0))

    featured = pd.concat([df, pd.DataFrame(grouped_frames, index=df.index)], axis=1)
    return featured.drop(columns=['unit_number', 'time_in_cycles'], errors='ignore')


def _xgboost_predict(featured: pd.DataFrame, scaler) -> float:
    last_row = featured.iloc[[-1]]
    ordered = last_row.reindex(columns=scaler.feature_names_in_, fill_value=0.0)
    scaled = scaler.transform(ordered)
    scaled_row = pd.DataFrame(scaled, columns=scaler.feature_names_in_)
    xgboost_model = loader.artifacts['regression_xgboost']
    return float(xgboost_model.predict(scaled_row)[0])


def _lstm_predict(featured: pd.DataFrame, scaler) -> float | None:
    """Runs the trailing window of engineered-feature rows through the
    trained LSTM regressor. Returns None (rather than raising) if the LSTM
    artifact isn't available, so a missing/corrupt LSTM checkpoint degrades
    to XGBoost-only instead of failing the whole /predict/rul request --
    the XGBoost ensemble member is the primary signal per docs/MODEL_CARDS.md.
    """
    state_dict = loader.artifacts.get('regression_lstm_state')
    if state_dict is None:
        return None

    ordered = featured.reindex(columns=scaler.feature_names_in_, fill_value=0.0)
    scaled = scaler.transform(ordered)

    seq = scaled[-LSTM_SEQUENCE_LENGTH:]
    if seq.shape[0] < LSTM_SEQUENCE_LENGTH:
        # Training pads short sequences at the START with zeros so the most
        # recent reading always lands in the last timestep (see
        # ml/models/lstm_rul.py: _prepare_sequences). Mirror that here.
        padded = np.zeros((LSTM_SEQUENCE_LENGTH, scaled.shape[1]), dtype=float)
        padded[-seq.shape[0]:] = seq
        seq = padded

    model = LSTMRegressor(input_size=seq.shape[1])
    model.load_state_dict(state_dict)
    model.eval()

    x = torch.tensor(seq, dtype=torch.float32).unsqueeze(0)  # (1, seq_len, n_features)
    with torch.no_grad():
        scaled_pred = model(x).item()
    return float(scaled_pred * LSTM_RUL_CAP)


def predict_rul(payload: dict) -> dict:
    loader.ensure_loaded()
    scaler = loader.artifacts['cmapss_scaler']
    history = payload.get('sensor_history', [])

    featured = _build_engineered_features(history)
    xgb_pred = _xgboost_predict(featured, scaler)

    try:
        lstm_pred = _lstm_predict(featured, scaler)
    except Exception:  # noqa: BLE001
        # Same reasoning as the `state_dict is None` branch above: a
        # shape/checkpoint mismatch on the secondary ensemble member
        # shouldn't take down the primary XGBoost-backed prediction.
        lstm_pred = None

    # Ensemble: average both members when the LSTM produced a usable
    # prediction, otherwise fall back to XGBoost alone.
    primary = xgb_pred if lstm_pred is None else (xgb_pred + lstm_pred) / 2
    model_used = 'xgboost' if lstm_pred is None else 'xgboost+lstm'

    return {
        'predicted_rul_cycles': primary,
        'predicted_rul_days': primary / 2,
        'recommended_maintenance_window_days': int(max(1, round(primary / 10))),
        'model_used': model_used,
        'xgboost_prediction': xgb_pred,
        'lstm_prediction': lstm_pred,
    }
