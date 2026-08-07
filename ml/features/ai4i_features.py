import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

from ml.config import ARTIFACTS_DIR


def build_ai4i_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    data = df.copy()
    data['temp_diff'] = data['Process temperature [K]'] - data['Air temperature [K]']
    data['power'] = data['Torque [Nm]'] * data['Rotational speed [rpm]']
    flag_cols = ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']
    data['failure_type'] = data[flag_cols].idxmax(axis=1)
    data.loc[(data['Machine failure'] == 1) & (data[flag_cols].sum(axis=1) == 0), 'failure_type'] = 'Unspecified'
    data.loc[(data['Machine failure'] == 0) & (data[flag_cols].sum(axis=1) > 0), 'failure_type'] = 'Unspecified'
    data.loc[(data['Machine failure'] == 1) & (data[flag_cols].sum(axis=1) > 1), 'failure_type'] = 'Unspecified'

    feature_cols = [col for col in data.columns if col not in {'Machine failure', 'failure_type'}]
    scaler = StandardScaler()
    scaled = data.copy()
    scaled[feature_cols] = scaler.fit_transform(data[feature_cols])
    joblib.dump(scaler, ARTIFACTS_DIR / 'classification' / 'ai4i_scaler.joblib')
    return scaled, {'feature_cols': feature_cols}
