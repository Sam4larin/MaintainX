"""Parses a user-uploaded equipment data file (CSV or Excel) into the same
shapes the existing /predict/* endpoints already accept.

This does not change the model contract at all -- it is purely a
convenience layer so a facility manager can drop in their own export
(from a CMMS, a data historian, or a spreadsheet) instead of hand-typing
values into the form. Detection is column-name based, tolerant of the
common real-world variants (spaces vs underscores, units in brackets,
different casing) rather than requiring an exact header match.
"""
import io
import re
from typing import Any

import numpy as np
import pandas as pd

SENSOR_COLS = [f'sensor_measurement_{i}' for i in range(1, 22)]

# Canonical AI4I columns -> the accepted aliases we'll match against,
# normalized (lowercase, non-alphanumeric stripped) before comparison.
AI4I_ALIASES: dict[str, list[str]] = {
    'air_temperature': ['airtemperaturek', 'airtemperature', 'airtemp'],
    'process_temperature': ['processtemperaturek', 'processtemperature', 'processtemp'],
    'rotational_speed': ['rotationalspeedrpm', 'rotationalspeed', 'speedrpm', 'rpm'],
    'torque': ['torquenm', 'torque'],
    'tool_wear': ['toolwearmin', 'toolwear'],
    'type': ['type', 'producttype'],
}

CMAPSS_TIME_ALIASES = ['timeincycles', 'cycle', 'cycles', 'timecycles']


def _normalize(name: str) -> str:
    return re.sub(r'[^a-z0-9]', '', str(name).lower())


CMAPSS_RAW_COLUMNS = (
    ['unit_number', 'time_in_cycles', 'operational_setting_1', 'operational_setting_2', 'operational_setting_3']
    + [f'sensor_measurement_{i}' for i in range(1, 22)]
)


def _read_any(filename: str, content: bytes) -> pd.DataFrame:
    lower = filename.lower()
    if lower.endswith('.xlsx') or lower.endswith('.xls'):
        return pd.read_excel(io.BytesIO(content))

    if lower.endswith('.txt'):
        # The NASA C-MAPSS distribution ships as headerless, whitespace-
        # delimited .txt with exactly 26 columns (unit, cycle, 3 operational
        # settings, 21 sensors) plus two trailing blank columns from a
        # trailing-space artifact in the original files. Detect that exact
        # shape before falling back to a generic CSV read, since a plain
        # pd.read_csv would otherwise treat the first data row as a header.
        text_df = pd.read_csv(io.BytesIO(content), sep=r'\s+', header=None, engine='python')
        # Drop fully-empty trailing columns caused by trailing whitespace.
        text_df = text_df.dropna(axis=1, how='all')
        if text_df.shape[1] == len(CMAPSS_RAW_COLUMNS):
            text_df.columns = CMAPSS_RAW_COLUMNS
            return text_df
        return text_df

    if lower.endswith('.csv'):
        return pd.read_csv(io.BytesIO(content))

    # Unknown extension: try CSV first, then the whitespace-delimited
    # headerless C-MAPSS shape, since some exports omit/mislabel extensions.
    try:
        return pd.read_csv(io.BytesIO(content))
    except Exception:  # noqa: BLE001
        pass
    try:
        text_df = pd.read_csv(io.BytesIO(content), sep=r'\s+', header=None, engine='python')
        text_df = text_df.dropna(axis=1, how='all')
        if text_df.shape[1] == len(CMAPSS_RAW_COLUMNS):
            text_df.columns = CMAPSS_RAW_COLUMNS
        return text_df
    except Exception as exc:  # noqa: BLE001
        raise ValueError(
            'Could not read this file. Upload a .csv or .xlsx export of your equipment data.'
        ) from exc


def _map_ai4i_columns(df: pd.DataFrame) -> dict[str, str]:
    """Returns {canonical_name: actual_column_name} for whichever AI4I
    columns are present, using normalized fuzzy matching."""
    normalized_lookup = {_normalize(col): col for col in df.columns}
    mapping: dict[str, str] = {}
    for canonical, aliases in AI4I_ALIASES.items():
        for alias in aliases:
            if alias in normalized_lookup:
                mapping[canonical] = normalized_lookup[alias]
                break
    return mapping


def _looks_like_cmapss(df: pd.DataFrame) -> bool:
    normalized_cols = {_normalize(c) for c in df.columns}
    sensor_hits = sum(1 for i in range(1, 22) if _normalize(f'sensor_measurement_{i}') in normalized_cols
                       or f'sensor{i}' in normalized_cols
                       or _normalize(f'sensor {i}') in normalized_cols)
    return sensor_hits >= 3


def _looks_like_ai4i(df: pd.DataFrame) -> bool:
    mapping = _map_ai4i_columns(df)
    # Require at least the core process variables to call it AI4I-shaped.
    required = {'air_temperature', 'process_temperature', 'rotational_speed', 'torque'}
    return required.issubset(mapping.keys())


def parse_uploaded_file(filename: str, content: bytes) -> dict[str, Any]:
    df = _read_any(filename, content)
    if df.empty:
        raise ValueError('The uploaded file has no data rows.')

    warnings: list[str] = []
    columns_found = [str(c) for c in df.columns]

    if _looks_like_ai4i(df):
        return _parse_ai4i(df, columns_found, warnings)
    if _looks_like_cmapss(df):
        return _parse_cmapss(df, columns_found, warnings)

    return {
        'detected_format': 'unknown',
        'row_count': int(len(df)),
        'warnings': [
            'Could not detect a known layout. Expected either machine process '
            'columns (air/process temperature, rotational speed, torque, tool wear) '
            'or sensor columns (sensor_measurement_1..21 with a cycle/time column).'
        ],
        'ai4i_rows': [],
        'sensor_history': [],
        'columns_found': columns_found,
    }


def _to_float(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors='coerce').fillna(default)


def _parse_ai4i(df: pd.DataFrame, columns_found: list[str], warnings: list[str]) -> dict[str, Any]:
    mapping = _map_ai4i_columns(df)
    missing = [c for c in ('air_temperature', 'process_temperature', 'rotational_speed', 'torque') if c not in mapping]
    if missing:
        raise ValueError(f'Missing required columns for machine telemetry: {missing}')

    air = _to_float(df[mapping['air_temperature']])
    process = _to_float(df[mapping['process_temperature']])
    speed = _to_float(df[mapping['rotational_speed']])
    torque = _to_float(df[mapping['torque']])

    if 'tool_wear' in mapping:
        wear = _to_float(df[mapping['tool_wear']])
    else:
        warnings.append('No tool-wear column found; defaulting tool wear to 0 for all rows.')
        wear = pd.Series(0.0, index=df.index)

    if 'type' in mapping:
        raw_type = df[mapping['type']]
        type_map = {'l': 0, 'm': 1, 'h': 2, 'low': 0, 'medium': 1, 'high': 2}
        type_numeric = raw_type.apply(
            lambda v: type_map.get(str(v).strip().lower(), None)
            if not str(v).strip().lstrip('-').isdigit()
            else int(v)
        )
        if type_numeric.isna().any():
            warnings.append('Some rows had an unrecognized machine "Type" value; defaulted to Medium (1).')
        type_numeric = type_numeric.fillna(1).astype(int)
    else:
        warnings.append('No machine "Type" column found (L/M/H); defaulting every row to Medium (1).')
        type_numeric = pd.Series(1, index=df.index)

    rows = []
    for i in range(len(df)):
        a, p, s, t, w = float(air.iloc[i]), float(process.iloc[i]), float(speed.iloc[i]), float(torque.iloc[i]), float(wear.iloc[i])
        rows.append({
            'Air_temperature_K': a,
            'Process_temperature_K': p,
            'Rotational_speed_rpm': s,
            'Torque_Nm': t,
            'Tool_wear_min': w,
            'Type': int(type_numeric.iloc[i]),
            'temp_diff': round(p - a, 4),
            'power': round(t * s, 4),
            'source_row': i + 1,
        })

    if len(rows) > 500:
        warnings.append(f'File had {len(rows)} rows; only the first 500 were parsed for preview/prediction.')
        rows = rows[:500]

    return {
        'detected_format': 'ai4i',
        'row_count': int(len(df)),
        'warnings': warnings,
        'ai4i_rows': rows,
        'sensor_history': [],
        'columns_found': columns_found,
    }


def _parse_cmapss(df: pd.DataFrame, columns_found: list[str], warnings: list[str]) -> dict[str, Any]:
    normalized_lookup = {_normalize(c): c for c in df.columns}

    # Real C-MAPSS exports contain many engine units concatenated in one
    # file (unit_number 1, 2, 3, ...). Mixing their cycles together would
    # produce a nonsensical single "history". If a unit column is present
    # and has more than one distinct value, default to the single unit with
    # the most recorded cycles (the most information-rich choice for a demo
    # prediction) and say so, rather than silently concatenating engines.
    unit_col = next((normalized_lookup[a] for a in ('unitnumber', 'unit', 'engineid', 'engine') if a in normalized_lookup), None)
    if unit_col is not None:
        unit_counts = df[unit_col].value_counts()
        if len(unit_counts) > 1:
            chosen_unit = unit_counts.idxmax()
            warnings.append(
                f'File contained {len(unit_counts)} engine units; using unit {chosen_unit} '
                f'({int(unit_counts.max())} cycles) since a single reading history is needed for one asset.'
            )
            df = df[df[unit_col] == chosen_unit].reset_index(drop=True)

    time_col = next((normalized_lookup[a] for a in CMAPSS_TIME_ALIASES if a in normalized_lookup), None)
    if time_col is None:
        warnings.append('No cycle/time column found; generating sequential cycle numbers starting at 1.')

    sensor_col_map: dict[str, str] = {}
    for i in range(1, 22):
        canonical = f'sensor_measurement_{i}'
        for alias in (_normalize(canonical), f'sensor{i}', _normalize(f'sensor {i}')):
            if alias in normalized_lookup:
                sensor_col_map[canonical] = normalized_lookup[alias]
                break

    missing_sensors = [f'sensor_measurement_{i}' for i in range(1, 22) if f'sensor_measurement_{i}' not in sensor_col_map]
    if missing_sensors:
        warnings.append(
            f'{len(missing_sensors)} of 21 sensor columns were not found and will be filled with 0: '
            f'{", ".join(missing_sensors[:5])}{"..." if len(missing_sensors) > 5 else ""}'
        )

    df = df.reset_index(drop=True)
    history: list[dict[str, Any]] = []
    for i in range(len(df)):
        reading: dict[str, Any] = {
            'time_in_cycles': int(pd.to_numeric(df[time_col].iloc[i], errors='coerce')) if time_col else i + 1,
        }
        for canonical in SENSOR_COLS:
            src = sensor_col_map.get(canonical)
            reading[canonical] = float(pd.to_numeric(df[src].iloc[i], errors='coerce')) if src else 0.0
        history.append(reading)

    if len(history) > 300:
        warnings.append(f'File had {len(history)} cycles; only the most recent 300 were used.')
        history = history[-300:]

    return {
        'detected_format': 'cmapss',
        'row_count': int(len(df)),
        'warnings': warnings,
        'ai4i_rows': [],
        'sensor_history': history,
        'columns_found': columns_found,
    }
