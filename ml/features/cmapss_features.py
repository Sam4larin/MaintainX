import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from ml.config import ARTIFACTS_DIR


def build_cmapss_features(train_df: pd.DataFrame, test_df: pd.DataFrame, rul_series: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    train = train_df.copy()
    test = test_df.copy()
    max_cycle_per_unit = train.groupby('unit_number')['time_in_cycles'].transform('max')
    train['rul'] = max_cycle_per_unit - train['time_in_cycles']

    # RUL_FD001.txt gives the true RUL only at each test engine's LAST observed
    # cycle (test engines are truncated mid-life, not run to failure). Earlier
    # cycles of the same engine have MORE cycles remaining, not the same amount.
    # BUG (fixed): previously assigned this single final-cycle value to every
    # row of the engine, producing a flat (non-decreasing) target across an
    # engine's life. That mismatched the correctly-decreasing train target and
    # was the root cause of negative R2 on the official test set.
    max_cycle_test_per_unit = test.groupby('unit_number')['time_in_cycles'].transform('max')
    unit_to_final_rul = dict(zip(sorted(test['unit_number'].unique()), rul_series.to_numpy()))
    final_rul_per_row = test['unit_number'].map(unit_to_final_rul)
    test['rul'] = final_rul_per_row + (max_cycle_test_per_unit - test['time_in_cycles'])

    sensor_cols = [c for c in train.columns if c.startswith('sensor_measurement_')]
    def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
        grouped_frames = {}
        for sensor in sensor_cols:
            g = df.groupby('unit_number')[sensor]
            grouped_frames[f'{sensor}_roll5_mean'] = g.transform(lambda s: s.rolling(5, min_periods=1).mean())
            grouped_frames[f'{sensor}_roll5_std'] = g.transform(lambda s: s.rolling(5, min_periods=1).std().fillna(0))
            grouped_frames[f'{sensor}_roll20_mean'] = g.transform(lambda s: s.rolling(20, min_periods=1).mean())
            grouped_frames[f'{sensor}_roll20_std'] = g.transform(lambda s: s.rolling(20, min_periods=1).std().fillna(0))
            baseline = g.transform(lambda s: s.iloc[:5].mean())
            grouped_frames[f'{sensor}_baseline_diff'] = df[sensor] - baseline
            grouped_frames[f'{sensor}_trend20'] = g.transform(lambda s: s.rolling(20, min_periods=1).apply(lambda w: w.iloc[-1] - w.iloc[0], raw=False).fillna(0))
            

        return pd.concat([df, pd.DataFrame(grouped_frames, index=df.index)], axis=1)

    train = add_rolling_features(train)
    test = add_rolling_features(test)

    
    train['rul'] = train['rul'].clip(upper=125)
    test['rul'] = test['rul'].clip(upper=125)
    feature_cols = [c for c in train.columns if c not in {'unit_number', 'time_in_cycles', 'rul'}]
    scaler = MinMaxScaler()
    train_scaled = train.copy()
    train_scaled[feature_cols] = scaler.fit_transform(train[feature_cols])
    test_scaled = test.copy()
    test_scaled[feature_cols] = scaler.transform(test[feature_cols])
    joblib.dump(scaler, ARTIFACTS_DIR / 'regression' / 'cmapss_scaler.joblib')
    return train_scaled, test_scaled, {'feature_cols': feature_cols}