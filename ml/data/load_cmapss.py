"""Load NASA C-MAPSS FD001 train/test files.

Source: NASA C-MAPSS turbofan engine degradation simulation (FD001 subset).
"""

from pathlib import Path
import pandas as pd

from ml.config import CMAPSS_TRAIN, CMAPSS_TEST, CMAPSS_RUL, SAMPLE_CMAPSS_TRAIN, SAMPLE_CMAPSS_TEST, SAMPLE_CMAPSS_RUL


def load_cmapss(path_train: Path | None = None, path_test: Path | None = None, path_rul: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    train_path = path_train or CMAPSS_TRAIN if CMAPSS_TRAIN.exists() else SAMPLE_CMAPSS_TRAIN
    test_path = path_test or CMAPSS_TEST if CMAPSS_TEST.exists() else SAMPLE_CMAPSS_TEST
    rul_path = path_rul or CMAPSS_RUL if CMAPSS_RUL.exists() else SAMPLE_CMAPSS_RUL

    train_df = pd.read_csv(train_path, sep=r'\s+', header=None)
    test_df = pd.read_csv(test_path, sep=r'\s+', header=None)
    rul_df = pd.read_csv(rul_path, header=None)

    columns = [
        'unit_number', 'time_in_cycles', 'operational_setting_1', 'operational_setting_2', 'operational_setting_3'
    ] + [f'sensor_measurement_{i}' for i in range(1, 22)]
    train_df.columns = columns
    test_df.columns = columns
    rul_df.columns = ['rul']
    return train_df, test_df, rul_df['rul']
