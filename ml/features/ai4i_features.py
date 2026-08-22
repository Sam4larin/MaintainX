import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from ml.config import ARTIFACTS_DIR


def build_ai4i_features(df: pd.DataFrame, raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, dict]:
    """
    df: the CLEANED AI4I data (flags already dropped) — used for model features.
    raw_df: the RAW AI4I data (flags still present) — used only to derive
            failure_type for dashboard/analytics display. Never merged into
            the model's training features (that would reintroduce leakage).
    """
    data = df.copy()
    data['temp_diff'] = data['Process_temperature'] - data['Air_temperature']
    data['power'] = data['Torque'] * data['Rotational_speed']

    # failure_type is derived from RAW flags, kept as a SEPARATE output —
    # for dashboard/reporting ("why did this machine fail?"), never fed
    # into the model as a feature (the flags are target leakage, per
    # clean_ai4i.py — see EDA notebook for the verification).
    flag_cols = ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']
    failure_type = raw_df[flag_cols].idxmax(axis=1)
    failure_type = failure_type.where(raw_df[flag_cols].sum(axis=1) == 1, other='Unspecified')
    failure_type = failure_type.where(raw_df['Machine failure'] == 1, other='No Failure')

    feature_cols = [col for col in data.columns if col != 'Machine_failure']
    scaler = StandardScaler()
    scaled = data.copy()
    scaled[feature_cols] = scaler.fit_transform(data[feature_cols])
    joblib.dump(scaler, ARTIFACTS_DIR / 'classification' / 'ai4i_scaler.joblib')
    return scaled, failure_type, {'feature_cols': feature_cols}