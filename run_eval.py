import json
import torch
import pandas as pd
from ml.config import ARTIFACTS_DIR, PROCESSED_DIR
from ml.models.forecasting_lstm import ForecastingLSTM, _prepare_sequences, evaluate_metrics

print("Loading forecasting config and model...")
forecasting_dir = ARTIFACTS_DIR / 'forecasting'
config = json.loads((forecasting_dir / 'model_config.json').read_text(encoding='utf-8'))

model = ForecastingLSTM(
    input_size=config['input_size'],
    n_targets=config['n_targets'],
    horizon=config['horizon']
)
model.load_state_dict(torch.load(forecasting_dir / 'forecasting_lstm.pt'))

print("Loading test features...")
test_features = pd.read_csv(PROCESSED_DIR / 'cmapss_test_features.csv')
print("Preparing test sequences...")
X_test_forecast, y_test_forecast, _, forecast_sensor_cols = _prepare_sequences(
    test_features,
    history_length=config['history_length'],
    horizon=config['horizon']
)

print("Evaluating metrics...")
forecasting_eval = evaluate_metrics(model, X_test_forecast, y_test_forecast, forecast_sensor_cols)
forecasting_metrics = json.loads((forecasting_dir / 'metrics.json').read_text(encoding='utf-8'))
forecasting_metrics.update(forecasting_eval)
(forecasting_dir / 'metrics.json').write_text(json.dumps(forecasting_metrics, indent=2), encoding='utf-8')

summary_path = ARTIFACTS_DIR / 'summary.json'
summary = json.loads(summary_path.read_text(encoding='utf-8'))
summary['forecasting'] = forecasting_metrics
summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')

print("Successfully evaluated forecasting metrics and updated metrics.json and summary.json!")
print(json.dumps(forecasting_eval, indent=2))


