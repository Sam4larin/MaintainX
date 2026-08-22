from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
RAW_DIR = DATA_DIR / 'raw'
SAMPLE_DIR = DATA_DIR / 'sample'
PROCESSED_DIR = DATA_DIR / 'processed'
ARTIFACTS_DIR = ROOT / 'ml' / 'artifacts'

CMAPSS_TRAIN = RAW_DIR / 'cmapss' / 'train_FD001.txt'
CMAPSS_TEST = RAW_DIR / 'cmapss' / 'test_FD001.txt'
CMAPSS_RUL = RAW_DIR / 'cmapss' / 'RUL_FD001.txt'
AI4I_FILE = RAW_DIR / 'ai4i' / 'ai4i2020.csv'

SAMPLE_CMAPSS_TRAIN = SAMPLE_DIR / 'train_FD001.txt'
SAMPLE_CMAPSS_TEST = SAMPLE_DIR / 'test_FD001.txt'
SAMPLE_CMAPSS_RUL = SAMPLE_DIR / 'RUL_FD001.txt'
SAMPLE_AI4I = SAMPLE_DIR / 'ai4i_sample.csv'

# Verified via EDA (ml/notebooks/01_eda_cmapss.ipynb): these columns have
# near-zero standard deviation (< 1e-6) in BOTH train and test splits of
# CMAPSS FD001, meaning they carry no discriminative signal for RUL prediction.
LOW_VARIANCE_SENSORS = [
    'operational_setting_3',
    'sensor_measurement_1',
    'sensor_measurement_5',
    'sensor_measurement_10',
    'sensor_measurement_16',
    'sensor_measurement_18',
    'sensor_measurement_19',
]
