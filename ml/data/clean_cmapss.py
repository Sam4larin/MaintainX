from pathlib import Path
import pandas as pd

from ml.config import LOW_VARIANCE_SENSORS


def clean_cmapss(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = train_df.copy()
    test = test_df.copy()

    low_var_cols = [col for col in train.columns if col in LOW_VARIANCE_SENSORS]
    train = train.drop(columns=low_var_cols)
    test = test.drop(columns=low_var_cols)
    return train, test
