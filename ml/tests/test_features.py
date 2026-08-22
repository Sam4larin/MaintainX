from ml.data.clean_ai4i import clean_ai4i
from ml.data.load_ai4i import load_ai4i
from ml.features.ai4i_features import build_ai4i_features


def test_ai4i_feature_engineering_creates_expected_columns():
    raw_ai4i = load_ai4i()
    ai4i = clean_ai4i(raw_ai4i)
    features, failure_type, metadata = build_ai4i_features(ai4i, raw_ai4i)
    assert 'temp_diff' in features.columns
    assert 'power' in features.columns
    assert 'failure_type' not in features.columns
    assert len(failure_type) == len(features)
    assert 'Machine_failure' in features.columns
    assert 'failure_type' not in metadata['feature_cols']
    assert 'Machine_failure' not in metadata['feature_cols']
    assert metadata['feature_cols']
