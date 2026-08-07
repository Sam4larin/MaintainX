import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from ml.config import ARTIFACTS_DIR


def build_cmapss_features(train_df: pd.DataFrame, test_df: pd.DataFrame, rul_series: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    train = train_df.copy()
    test = test_df.copy()
    train['rul'] = rul_series.iloc[:len(train)].to_numpy()
    test['rul'] = 0

    for unit in sorted(train['unit_number'].unique()):
        unit_rows = train.loc[train['unit_number'] == unit].copy()
        for sensor in [c for c in train.columns if c.startswith('sensor_measurement_')]:
            train.loc[unit_rows.index, f'{sensor}_roll5_mean'] = unit_rows[sensor].rolling(5, min_periods=1).mean()
            train.loc[unit_rows.index, f'{sensor}_roll5_std'] = unit_rows[sensor].rolling(5, min_periods=1).std().fillna(0)
            train.loc[unit_rows.index, f'{sensor}_roll20_mean'] = unit_rows[sensor].rolling(20, min_periods=1).mean()
            train.loc[unit_rows.index, f'{sensor}_roll20_std'] = unit_rows[sensor].rolling(20, min_periods=1).std().fillna(0)

    train['rul'] = train['rul'].clip(upper=125)
    feature_cols = [c for c in train.columns if c not in {'unit_number', 'time_in_cycles', 'rul'}]
    scaler = MinMaxScaler()
    train_scaled = train.copy()
    train_scaled[feature_cols] = scaler.fit_transform(train[feature_cols])
    test_scaled = test.copy()
    test_scaled[feature_cols] = scaler.transform(test[feature_cols])
    joblib.dump(scaler, ARTIFACTS_DIR / 'regression' / 'cmapss_scaler.joblib')
    return train_scaled, test_scaled, {'feature_cols': feature_cols}
