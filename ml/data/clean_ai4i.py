import pandas as pd


def clean_ai4i(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned = cleaned.drop(columns=['UDI', 'Product ID'], errors='ignore')
    cleaned['Type'] = cleaned['Type'].astype(str).str.strip()
    type_map = {'L': 0, 'M': 1, 'H': 2}
    cleaned['Type'] = cleaned['Type'].map(type_map).fillna(1)
    if cleaned.isna().any().any():
        raise ValueError('Unexpected missing values detected in AI4I data')
    return cleaned
