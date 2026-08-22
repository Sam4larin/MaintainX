import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from ml.data.clean_ai4i import clean_ai4i
from ml.data.clean_cmapss import clean_cmapss
from ml.data.load_ai4i import load_ai4i
from ml.data.load_cmapss import load_cmapss
from ml.features.ai4i_features import build_ai4i_features
from ml.features.cmapss_features import build_cmapss_features
from ml.models.anomaly_autoencoder import train as train_autoencoder
from ml.models.anomaly_isolation_forest import train as train_iforest
from ml.models.classification import train as train_classification
from ml.models.forecasting_lstm import train as train_forecasting
from ml.models.lstm_rul import train as train_lstm
from ml.models.regression import train as train_regression


def test_models_train_and_predict_smoke():
    ai4i_raw = load_ai4i()
    ai4i = clean_ai4i(ai4i_raw)
    ai4i_features, failure_type, _ = build_ai4i_features(ai4i, ai4i_raw)
    ai4i_features['failure_type'] = failure_type
    train_classification(ai4i_features, output_dir='tmp')
    train_iforest(ai4i_features, output_dir='tmp')
    train_autoencoder(ai4i_features, output_dir='tmp')

    train_df, test_df, rul = load_cmapss()
    train_df, test_df = clean_cmapss(train_df, test_df)
    train_features, test_features, _ = build_cmapss_features(train_df, test_df, rul)
    train_regression(train_features, test_features, output_dir='tmp')
    train_lstm(train_features, test_features, output_dir='tmp')
    train_forecasting(train_features, output_dir='tmp')