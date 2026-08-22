import pandas as pd


def clean_ai4i(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    # UDI, Product ID: row identifiers, not predictive features.
    # TWF, HDF, PWF, OSF, RNF: individual failure-mode flags, this was verified via EDA
    # Must be excluded so the model learns from sensor readings, not from the failure report itself.
    cleaned = cleaned.drop(columns=['UDI', 'Product ID', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF'], errors='ignore')
    cleaned['Type'] = cleaned['Type'].astype(str).str.strip()
    type_map = {'L': 0, 'M': 1, 'H': 2}
    cleaned['Type'] = cleaned['Type'].map(type_map).fillna(1)
    cleaned.columns = (
        cleaned.columns
        .str.replace(r'\s*\[.*?\]', '', regex=True)
        .str.strip()
        .str.replace(' ', '_')
    )
    
    if cleaned.isna().any().any():
        raise ValueError('Unexpected missing values detected in AI4I data')
    return cleaned
