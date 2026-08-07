from ml.data.clean_ai4i import clean_ai4i
from ml.data.load_ai4i import load_ai4i
from ml.features.ai4i_features import build_ai4i_features


def test_ai4i_feature_engineering_creates_expected_columns():
    ai4i = clean_ai4i(load_ai4i())
    features, metadata = build_ai4i_features(ai4i)
    assert 'temp_diff' in features.columns
    assert 'power' in features.columns
    assert 'failure_type' in features.columns
    assert 'Machine failure' in features.columns
    assert metadata['feature_cols']
