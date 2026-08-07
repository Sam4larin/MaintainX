def forecast(payload: dict) -> dict:
    history = payload.get('sensor_history', [])
    sensor_names = sorted({key for item in history for key in item.keys() if key != 'time_in_cycles'})
    forecasted = {name: [float(item.get(name, 0.0)) for item in history[-5:]] for name in sensor_names}
    return {
        'forecasted_cycles': list(range(1, 6)),
        'forecasted_sensor_values': {name: [value + 0.1 * idx for idx, value in enumerate(values)] for name, values in forecasted.items()},
    }
