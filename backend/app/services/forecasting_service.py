import pandas as pd
import torch

from backend.app.services.cmapss_feature_builder import build_engineered_features
from backend.app.services.model_loader import loader
from ml.models.forecasting_lstm import ForecastingLSTM


def forecast(payload: dict) -> dict:
    loader.ensure_loaded()
    history = payload.get('sensor_history', [])
    config = loader.artifacts['forecasting_config']
    history_length = config['history_length']
    feature_cols = config['feature_cols']
    sensor_cols = config['sensor_cols']

    # Build the same engineered features (rolling/trend/baseline-diff) used
    # at training time from the raw sensor history the caller actually
    # sends -- this MUST call build_engineered_features(), not read
    # feature_cols directly from the raw payload, or every real request
    # will fail with a missing-columns error (this exact regression has
    # happened more than once in this project's history -- see
    # docs/DECISIONS.md #13).
    featured = build_engineered_features(history)

    if len(featured) < history_length:
        raise ValueError(
            f'sensor_history must contain at least {history_length} cycles for forecasting '
            f'(got {len(featured)}).'
        )

    missing = [c for c in feature_cols if c not in featured.columns]
    if missing:
        raise ValueError(f'sensor_history rows are missing required columns after feature engineering: {missing}')

    window = featured[feature_cols].to_numpy(dtype=float)[-history_length:]
    X = torch.tensor(window[None, :, :], dtype=torch.float32)

    model = ForecastingLSTM(input_size=config['input_size'], n_targets=config['n_targets'], horizon=config['horizon'])
    model.load_state_dict(loader.artifacts['forecasting_lstm_state'])
    model.eval()
    with torch.no_grad():
        pred = model(X).numpy()[0]

    forecasted_sensor_values = {
        sensor: [float(pred[step, i]) for step in range(config['horizon'])]
        for i, sensor in enumerate(sensor_cols)
    }
    return {
        'forecasted_cycles': list(range(1, config['horizon'] + 1)),
        'forecasted_sensor_values': forecasted_sensor_values,
    }
