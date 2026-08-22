import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
import pandas as pd

from ml.config import ARTIFACTS_DIR, PROCESSED_DIR
from ml.data.clean_ai4i import clean_ai4i
from ml.data.clean_cmapss import clean_cmapss
from ml.data.load_ai4i import load_ai4i
from ml.data.load_cmapss import load_cmapss
from ml.evaluation.plots import save_anomaly_plot, save_confusion_matrix, save_regression_plot
from ml.features.ai4i_features import build_ai4i_features
from ml.features.cmapss_features import build_cmapss_features
from ml.models.anomaly_autoencoder import train as train_autoencoder
from ml.models.anomaly_isolation_forest import train as train_iforest
from ml.models.classification import train as train_classification
from ml.models.forecasting_lstm import train as train_forecasting
from ml.models.lstm_rul import train as train_lstm
from ml.models.regression import train as train_regression


def run_pipeline():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ai4i_raw = load_ai4i()
    ai4i_df = clean_ai4i(ai4i_raw)
    ai4i_features, failure_type, _ = build_ai4i_features(ai4i_df, ai4i_raw)
    ai4i_features['failure_type'] = failure_type
    ai4i_features.to_csv(PROCESSED_DIR / 'ai4i_features.csv', index=False)

    train_df, test_df, rul_series = load_cmapss()
    train_df, test_df = clean_cmapss(train_df, test_df)
    train_features, test_features, _ = build_cmapss_features(train_df, test_df, rul_series)
    train_features.to_csv(PROCESSED_DIR / 'cmapss_train_features.csv', index=False)
    test_features.to_csv(PROCESSED_DIR / 'cmapss_test_features.csv', index=False)

    output_dir = ARTIFACTS_DIR / 'classification'
    output_dir.mkdir(parents=True, exist_ok=True)
    classification_model, multi_model, class_metrics = train_classification(ai4i_features, output_dir=output_dir)
    save_confusion_matrix((ai4i_features['Machine_failure'] > 0).astype(int), classification_model.predict(ai4i_features.drop(columns=['Machine_failure', 'failure_type'])), output_dir)

    regression_dir = ARTIFACTS_DIR / 'regression'
    regression_dir.mkdir(parents=True, exist_ok=True)
    reg_model, reg_metrics = train_regression(train_features, test_features, output_dir=regression_dir)
    save_regression_plot(test_features['rul'], reg_model.predict(test_features.drop(columns=['rul', 'unit_number', 'time_in_cycles'])), regression_dir)

    lstm_model, lstm_metrics = train_lstm(train_features, test_features, output_dir=regression_dir)

    anomaly_dir = ARTIFACTS_DIR / 'anomaly'
    anomaly_dir.mkdir(parents=True, exist_ok=True)
    iforest_model, anomaly_metrics = train_iforest(ai4i_features, output_dir=anomaly_dir)
    autoencoder_model, autoencoder_threshold, autoencoder_metrics = train_autoencoder(ai4i_features, output_dir=anomaly_dir)
    save_anomaly_plot((iforest_model.decision_function(ai4i_features.drop(columns=['Machine_failure', 'failure_type'])) * -1), (ai4i_features['Machine_failure'] == 1).astype(int), anomaly_dir)

    forecasting_dir = ARTIFACTS_DIR / 'forecasting'
    forecasting_dir.mkdir(parents=True, exist_ok=True)
    forecasting_model = train_forecasting(train_features, output_dir=forecasting_dir)
    forecasting_metrics = json.loads((forecasting_dir / 'metrics.json').read_text(encoding='utf-8'))

    meta = {
        'classification': class_metrics,
        'regression': {'xgboost': reg_metrics, 'lstm': lstm_metrics},
        'anomaly': {'isolation_forest': anomaly_metrics, 'autoencoder': autoencoder_metrics},
        'forecasting': forecasting_metrics,
    }
    (ARTIFACTS_DIR / 'summary.json').write_text(json.dumps(meta), encoding='utf-8')


def main():
    run_pipeline()
    print('Pipeline complete. Artifacts written to', ARTIFACTS_DIR)


if __name__ == '__main__':
    main()