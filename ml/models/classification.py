import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, average_precision_score,)
from sklearn.model_selection import StratifiedKFold, train_test_split
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from ml.config import ARTIFACTS_DIR


def train(df: pd.DataFrame, output_dir: Path | None | str = None, n_splits: int = 5):
    output_dir = Path(output_dir) if output_dir is not None else ARTIFACTS_DIR / 'classification'
    output_dir.mkdir(parents=True, exist_ok=True)

    features = [c for c in df.columns if c not in {'Machine_failure', 'failure_type'}]
    X = df[features]
    y = df['Machine_failure']

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    fold_metrics = {'accuracy': [], 'precision': [], 'recall': [], 'f1': [], 'roc_auc': [], 'pr_auc': []}

    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum() if y_train.sum() > 0 else 1.0

        fold_model = xgb.XGBClassifier(
            n_estimators=20, max_depth=3, learning_rate=0.1,
            scale_pos_weight=scale_pos_weight, random_state=42,
        )
        fold_model.fit(X_train, y_train)
        preds = fold_model.predict(X_test)
        probs = fold_model.predict_proba(X_test)[:, 1]

        fold_metrics['accuracy'].append(accuracy_score(y_test, preds))
        fold_metrics['precision'].append(precision_score(y_test, preds, zero_division=0))
        fold_metrics['recall'].append(recall_score(y_test, preds, zero_division=0))
        fold_metrics['f1'].append(f1_score(y_test, preds, zero_division=0))
        fold_metrics['roc_auc'].append(roc_auc_score(y_test, probs))
        fold_metrics['pr_auc'].append(average_precision_score(y_test, probs))

    metrics = {
        name: {'mean': float(np.mean(vals)), 'std': float(np.std(vals)), 'folds': [float(v) for v in vals]}
        for name, vals in fold_metrics.items()
    }

    scale_pos_weight_full = (len(y) - y.sum()) / y.sum() if y.sum() > 0 else 1.0
    model = xgb.XGBClassifier(
        n_estimators=20, max_depth=3, learning_rate=0.1,
        scale_pos_weight=scale_pos_weight_full, random_state=42,
    )
    model.fit(X, y)
    joblib.dump(model, output_dir / 'binary_classifier.joblib')

    failed_mask = df['Machine_failure'] == 1
    X_failed = X[failed_mask]
    y_multi = df.loc[failed_mask, 'failure_type']

    multi_metrics = {'note': 'Only 339 failure examples total; treat as directional, not precise.'}
    num_classes = y_multi.nunique()
    if num_classes >= 2 and len(y_multi) >= 20:
        y_multi_encoded, class_labels = pd.factorize(y_multi)
        X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(
            X_failed, y_multi_encoded, test_size=0.2, random_state=42,
            stratify=y_multi_encoded if min(np.bincount(y_multi_encoded)) >= 2 else None,
        )
        multi_model = xgb.XGBClassifier(
            n_estimators=20, max_depth=3, learning_rate=0.1,
            objective='multi:softprob', num_class=num_classes, random_state=42,
        )
        multi_model.fit(X_train_m, y_train_m)
        multi_preds = multi_model.predict(X_test_m)
        multi_metrics['macro_f1'] = f1_score(y_test_m, multi_preds, average='macro')
        multi_metrics['class_labels'] = list(class_labels)
        joblib.dump(multi_model, output_dir / 'multiclass_classifier.joblib')
        joblib.dump(class_labels, output_dir / 'multiclass_labels.joblib')
    else:
        multi_model = None

    (output_dir / 'metrics.json').write_text(
        json.dumps({'binary_cv': metrics, 'multiclass': multi_metrics}, indent=2),
        encoding='utf-8',
    )
    return model, multi_model, metrics


def evaluate(model, X_test: pd.DataFrame):
    return model.predict(X_test)