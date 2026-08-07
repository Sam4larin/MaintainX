import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / 'data' / 'raw'
SAMPLE_DIR = ROOT / 'data' / 'sample'


def ensure_sample_data():
    if not (SAMPLE_DIR / 'ai4i_sample.csv').exists():
        (SAMPLE_DIR / 'ai4i_sample.csv').write_text(
            'UDI,Product ID,Type,Air temperature [K],Process temperature [K],Rotational speed [rpm],Torque [Nm],Tool wear [min],Machine failure,TWF,HDF,PWF,OSF,RNF\n'
            '1,M1, L, 298.2, 308.7, 1551, 42.8, 0, 0, 0, 0, 0, 0, 0\n'
            '2,M2, M, 298.1, 308.5, 1408, 28.6, 3, 0, 0, 0, 0, 0, 0\n'
            '3,M3, H, 298.5, 308.9, 1498, 35.4, 5, 1, 0, 1, 0, 0, 0\n',
            encoding='utf-8',
        )
    if not (SAMPLE_DIR / 'train_FD001.txt').exists():
        (SAMPLE_DIR / 'train_FD001.txt').write_text(
            '1 1 0.7 0.0 100.0 518.67 641.82 1589.70 1400.60 14.62 21.61 554.36 2388.06 904.99 1.30 47.47 521.66 2388.02 813.41 8.93 0.03 0.00\n'
            '1 2 0.7 0.0 100.0 518.67 642.15 1589.70 1400.60 14.62 21.61 554.36 2388.06 904.99 1.30 47.47 521.66 2388.02 813.41 8.93 0.03 0.00\n'
            '1 3 0.7 0.0 100.0 518.67 642.35 1589.70 1400.60 14.62 21.61 554.36 2388.06 904.99 1.30 47.47 521.66 2388.02 813.41 8.93 0.03 0.00\n',
            encoding='utf-8',
        )
    if not (SAMPLE_DIR / 'test_FD001.txt').exists():
        (SAMPLE_DIR / 'test_FD001.txt').write_text(
            '1 1 0.7 0.0 100.0 518.67 641.82 1589.70 1400.60 14.62 21.61 554.36 2388.06 904.99 1.30 47.47 521.66 2388.02 813.41 8.93 0.03 0.00\n',
            encoding='utf-8',
        )
    if not (SAMPLE_DIR / 'RUL_FD001.txt').exists():
        (SAMPLE_DIR / 'RUL_FD001.txt').write_text('112\n', encoding='utf-8')


def main():
    ensure_sample_data()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / 'cmapss').mkdir(parents=True, exist_ok=True)
    (RAW_DIR / 'ai4i').mkdir(parents=True, exist_ok=True)
    print('Sample data created at', SAMPLE_DIR)


if __name__ == '__main__':
    main()
