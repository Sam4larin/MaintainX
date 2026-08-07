import json
from pathlib import Path

import joblib
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, average_precision_score
from sklearn.model_selection import train_test_split

from ml.config import ARTIFACTS_DIR


def train(df: pd.DataFrame, output_dir: Path | None | str = None):
    output_dir = Path(output_dir) if output_dir is not None else ARTIFACTS_DIR / 'classification'
    output_dir.mkdir(parents=True, exist_ok=True)

    features = [c for c in df.columns if c not in {'Machine failure', 'failure_type'}]
    X = df[features]
    y = df['Machine failure']
    scale_pos_weight = (len(y) - y.sum()) / y.sum() if y.sum() > 0 else 1.0

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    model = xgb.XGBClassifier(n_estimators=20, max_depth=3, learning_rate=0.1, scale_pos_weight=scale_pos_weight, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    metrics = {
        'accuracy': accuracy_score(y_test, preds),
        'precision': precision_score(y_test, preds, zero_division=0),
        'recall': recall_score(y_test, preds, zero_division=0),
        'f1': f1_score(y_test, preds, zero_division=0),
        'roc_auc': roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]),
        'pr_auc': average_precision_score(y_test, model.predict_proba(X_test)[:, 1]),
    }
    joblib.dump(model, output_dir / 'binary_classifier.joblib')

    y_multi = df['failure_type']
    X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(X, y_multi, test_size=0.2, stratify=y_multi, random_state=42)
    multi_model = xgb.XGBClassifier(n_estimators=20, max_depth=3, learning_rate=0.1, objective='multi:softprob', num_class=4, random_state=42)
    multi_model.fit(X_train_m, y_train_m)
    multi_preds = multi_model.predict(X_test_m)
    multi_metrics = {
        'macro_f1': f1_score(y_test_m, multi_preds, average='macro'),
    }
    joblib.dump(multi_model, output_dir / 'multiclass_classifier.joblib')

    (output_dir / 'metrics.json').write_text(json.dumps({**metrics, **{'multi_class_macro_f1': multi_metrics['macro_f1']}}), encoding='utf-8')
    return model, multi_model, metrics


def evaluate(model, X_test: pd.DataFrame):
    return model.predict(X_test)
