"""Load the AI4I 2020 predictive maintenance dataset.

Source: UCI Machine Learning Repository, AI4I 2020 Predictive Maintenance Dataset.
"""

from pathlib import Path
import pandas as pd

from ml.config import AI4I_FILE, SAMPLE_AI4I


def load_ai4i(path: Path | None = None) -> pd.DataFrame:
    data_path = path or AI4I_FILE if AI4I_FILE.exists() else SAMPLE_AI4I
    return pd.read_csv(data_path)
