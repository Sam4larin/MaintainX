import json
from pathlib import Path

import joblib
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from ml.config import ARTIFACTS_DIR


def train(train_df: pd.DataFrame, test_df: pd.DataFrame, output_dir: Path | None | str = None):
    output_dir = Path(output_dir) if output_dir is not None else ARTIFACTS_DIR / 'regression'
    output_dir.mkdir(parents=True, exist_ok=True)

    drop_cols = ['rul', 'unit_number', 'time_in_cycles']
    X_train = train_df.drop(columns=drop_cols)
    y_train = train_df['rul']
    X_test = test_df.drop(columns=drop_cols)
    y_test = test_df['rul']

    model = xgb.XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    metrics = {
        'rmse': root_mean_squared_error(y_test, pred),
        'mae': mean_absolute_error(y_test, pred),
        'r2': r2_score(y_test, pred),
    }
    joblib.dump(model, output_dir / 'xgboost_rul.joblib')
    (output_dir / 'metrics.json').write_text(json.dumps(metrics), encoding='utf-8')
    return model, metrics


def evaluate(model, X_test: pd.DataFrame):
    return model.predict(X_test)
