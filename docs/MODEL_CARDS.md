# Model Cards

## Failure classification (AI4I)
- Purpose: predict whether a machine will fail soon.
- Input features: AI4I process parameters and derived temperature/power metrics.
- Metrics: trained on the sample data and saved in ml/artifacts/classification/metrics.json.

## RUL regression (C-MAPSS)
- Purpose: estimate remaining useful life.
- Input features: cleaned C-MAPSS sensor and operational setting features with rolling statistics.
- Metrics: trained on the sample data and saved in ml/artifacts/regression/metrics.json.

## Anomaly detection
- Purpose: flag unusual behavior using isolation forests and autoencoders.
- Input features: AI4I process features.
- Metrics: evaluated against failure proxy labels from the sample data.

## Forecasting LSTM
- Purpose: forecast future sensor trajectories for a machine.
- Input features: sliding windows of recent C-MAPSS sensor readings.
- Metrics: training artifacts saved to ml/artifacts/forecasting/.
