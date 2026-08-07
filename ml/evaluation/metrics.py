from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, mean_absolute_error, mean_squared_error, r2_score


def binary_classification_metrics(y_true: Iterable[int], y_pred: Iterable[int]) -> dict:
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    return {
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
    }


def regression_metrics(y_true: Iterable[float], y_pred: Iterable[float]) -> dict:
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    return {
        'rmse': mean_squared_error(y_true, y_pred, squared=False),
        'mae': mean_absolute_error(y_true, y_pred),
        'r2': r2_score(y_true, y_pred),
    }


def nasa_score(y_true: Iterable[float], y_pred: Iterable[float]) -> float:
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    diff = y_pred - y_true
    score = np.sum(np.where(diff < 0, np.exp(-diff / 13) - 1, np.exp(diff / 10) - 1))
    return float(score)
