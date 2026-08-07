import pandas as pd

from ml.data.load_ai4i import load_ai4i
from ml.data.load_cmapss import load_cmapss
from ml.data.clean_ai4i import clean_ai4i
from ml.data.clean_cmapss import clean_cmapss


def test_loaders_return_expected_shapes():
    ai4i = load_ai4i()
    assert isinstance(ai4i, pd.DataFrame)
    assert ai4i.shape[0] > 0

    train_df, test_df, rul = load_cmapss()
    assert isinstance(train_df, pd.DataFrame)
    assert isinstance(test_df, pd.DataFrame)
    assert len(rul) > 0

    cleaned_ai4i = clean_ai4i(ai4i)
    assert 'UDI' not in cleaned_ai4i.columns

    cleaned_train, cleaned_test = clean_cmapss(train_df, test_df)
    assert cleaned_train.shape[0] == train_df.shape[0]
