import pandas as pd
import torch

from backend.app.services.model_loader import loader
from ml.models.forecasting_lstm import ForecastingLSTM


def forecast(payload: dict) -> dict:
    loader.ensure_loaded()
    history = payload.get('sensor_history', [])
    config = loader.artifacts['forecasting_config']
    history_length = config['history_length']
    feature_cols = config['feature_cols']
    sensor_cols = config['sensor_cols']

    if len(history) < history_length:
        raise ValueError(
            f'sensor_history must contain at least {history_length} cycles for forecasting '
            f'(got {len(history)}).'
        )

    df = pd.DataFrame(history).sort_values('time_in_cycles').reset_index(drop=True)
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(f'sensor_history rows are missing required columns: {missing}')

    window = df[feature_cols].to_numpy(dtype=float)[-history_length:]
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