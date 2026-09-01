import pandas as pd

SENSOR_COLS = [f'sensor_measurement_{i}' for i in range(1, 22)]


def build_engineered_features(history: list[dict]) -> pd.DataFrame:
    """Reconstruct the same engineered features used at training time
    (ml/features/cmapss_features.py: add_rolling_features) from a single
    engine's raw sensor history: rolling5/20 mean+std, baseline-diff, and
    trend20 per sensor.

    Returns a full per-cycle dataframe (not just the last row), so callers
    needing a single point-in-time snapshot (regression) can take the last
    row, and callers needing a window of recent engineered rows
    (forecasting) can take a tail slice.

    Raw sensor history is the correct API contract here: a real caller
    (or this frontend) has raw sensor readings, not pre-engineered rolling
    statistics -- computing those is this service's job, not the caller's.

    NOTE: rolling/trend windows need real history to be meaningful (roll20
    needs up to 20 prior cycles). A short history will still produce valid
    output (rolling ops use min_periods=1, matching training), but accuracy
    degrades for very early-life engines with few recorded cycles, same as
    it would for a real too-short test engine.
    """
    if not history:
        raise ValueError('sensor_history must contain at least one reading')

    df = pd.DataFrame(history).sort_values('time_in_cycles').reset_index(drop=True)
    missing_sensors = [c for c in SENSOR_COLS if c not in df.columns]
    if missing_sensors:
        raise ValueError(f'sensor_history rows are missing required sensor columns: {missing_sensors}')

    # FD001 (the CMAPSS subset this project trains on) is single-operating-
    # condition data: operational_setting_1/2 are ~0 with negligible
    # variance (std ~0.002) across the entire real dataset. Default to 0
    # when a caller doesn't supply them, rather than requiring every caller
    # to know and send FD001-specific near-constant values. Callers that do
    # have real values can still pass operational_setting_1/2 explicitly.
    for col in ('operational_setting_1', 'operational_setting_2'):
        if col not in df.columns:
            df[col] = 0.0

    # Single-engine history -> a constant unit_number lets us reuse the exact
    # same groupby-based rolling logic as training without duplicating it.
    df['unit_number'] = 0

    grouped_frames = {}
    for sensor in SENSOR_COLS:
        g = df.groupby('unit_number')[sensor]
        grouped_frames[f'{sensor}_roll5_mean'] = g.transform(lambda s: s.rolling(5, min_periods=1).mean())
        grouped_frames[f'{sensor}_roll5_std'] = g.transform(lambda s: s.rolling(5, min_periods=1).std().fillna(0))
        grouped_frames[f'{sensor}_roll20_mean'] = g.transform(lambda s: s.rolling(20, min_periods=1).mean())
        grouped_frames[f'{sensor}_roll20_std'] = g.transform(lambda s: s.rolling(20, min_periods=1).std().fillna(0))
        baseline = g.transform(lambda s: s.iloc[:5].mean())
        grouped_frames[f'{sensor}_baseline_diff'] = df[sensor] - baseline
        grouped_frames[f'{sensor}_trend20'] = g.transform(lambda s: s.rolling(20, min_periods=1).apply(lambda w: w.iloc[-1] - w.iloc[0], raw=False).fillna(0))

    featured = pd.concat([df, pd.DataFrame(grouped_frames, index=df.index)], axis=1)
    return featured.drop(columns=['unit_number'], errors='ignore')
