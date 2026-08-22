import numpy as np
import pandas as pd

from backend.app.services.model_loader import loader

SENSOR_COLS = [f'sensor_measurement_{i}' for i in range(1, 22)]


def _build_features_for_history(history: list[dict]) -> pd.DataFrame:
    """Reconstruct the same engineered features used at training time
    (ml/features/cmapss_features.py: add_rolling_features) from a single
    engine's raw sensor history, then apply the fitted training-time
    scaler. Returns one row: the features for the LAST cycle in history,
    since that's the point we want to predict RUL from.
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
    last_row = featured.iloc[[-1]].drop(columns=['unit_number', 'time_in_cycles'], errors='ignore')
    return last_row


def predict_rul(payload: dict) -> dict:
    loader.ensure_loaded()
    xgboost_model = loader.artifacts['regression_xgboost']
    scaler = loader.artifacts['cmapss_scaler']
    history = payload.get('sensor_history', [])

    features_row = _build_features_for_history(history)
    ordered = features_row.reindex(columns=scaler.feature_names_in_, fill_value=0.0)
    scaled = scaler.transform(ordered)
    scaled_row = pd.DataFrame(scaled, columns=scaler.feature_names_in_)

    xgb_pred = float(xgboost_model.predict(scaled_row)[0])
    return {
        'predicted_rul_cycles': xgb_pred,
        'predicted_rul_days': xgb_pred / 2,
        'recommended_maintenance_window_days': int(max(1, round(xgb_pred / 10))),
        'model_used': 'xgboost',
        'xgboost_prediction': xgb_pred,
        'lstm_prediction': None,
    }