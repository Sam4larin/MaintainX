import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

@pytest.fixture
def valid_rul_payload():
    return {
        "sensor_history": [
        {
                "time_in_cycles": 1,
                "operational_setting_1": 0.0023,
                "operational_setting_2": 0.0003,
                "operational_setting_3": 100.0,
                "sensor_measurement_1": 518.67,
                "sensor_measurement_2": 643.02,
                "sensor_measurement_3": 1585.29,
                "sensor_measurement_4": 1398.21,
                "sensor_measurement_5": 14.62,
                "sensor_measurement_6": 21.61,
                "sensor_measurement_7": 553.9,
                "sensor_measurement_8": 2388.04,
                "sensor_measurement_9": 9050.17,
                "sensor_measurement_10": 1.3,
                "sensor_measurement_11": 47.2,
                "sensor_measurement_12": 521.72,
                "sensor_measurement_13": 2388.03,
                "sensor_measurement_14": 8125.55,
                "sensor_measurement_15": 8.4052,
                "sensor_measurement_16": 0.03,
                "sensor_measurement_17": 392,
                "sensor_measurement_18": 2388,
                "sensor_measurement_19": 100.0,
                "sensor_measurement_20": 38.86,
                "sensor_measurement_21": 23.3735
        },
        {
                "time_in_cycles": 2,
                "operational_setting_1": -0.0027,
                "operational_setting_2": -0.0003,
                "operational_setting_3": 100.0,
                "sensor_measurement_1": 518.67,
                "sensor_measurement_2": 641.71,
                "sensor_measurement_3": 1588.45,
                "sensor_measurement_4": 1395.42,
                "sensor_measurement_5": 14.62,
                "sensor_measurement_6": 21.61,
                "sensor_measurement_7": 554.85,
                "sensor_measurement_8": 2388.01,
                "sensor_measurement_9": 9054.42,
                "sensor_measurement_10": 1.3,
                "sensor_measurement_11": 47.5,
                "sensor_measurement_12": 522.16,
                "sensor_measurement_13": 2388.06,
                "sensor_measurement_14": 8139.62,
                "sensor_measurement_15": 8.3803,
                "sensor_measurement_16": 0.03,
                "sensor_measurement_17": 393,
                "sensor_measurement_18": 2388,
                "sensor_measurement_19": 100.0,
                "sensor_measurement_20": 39.02,
                "sensor_measurement_21": 23.3916
        },
        {
                "time_in_cycles": 3,
                "operational_setting_1": 0.0003,
                "operational_setting_2": 0.0001,
                "operational_setting_3": 100.0,
                "sensor_measurement_1": 518.67,
                "sensor_measurement_2": 642.46,
                "sensor_measurement_3": 1586.94,
                "sensor_measurement_4": 1401.34,
                "sensor_measurement_5": 14.62,
                "sensor_measurement_6": 21.61,
                "sensor_measurement_7": 554.11,
                "sensor_measurement_8": 2388.05,
                "sensor_measurement_9": 9056.96,
                "sensor_measurement_10": 1.3,
                "sensor_measurement_11": 47.5,
                "sensor_measurement_12": 521.97,
                "sensor_measurement_13": 2388.03,
                "sensor_measurement_14": 8130.1,
                "sensor_measurement_15": 8.4441,
                "sensor_measurement_16": 0.03,
                "sensor_measurement_17": 393,
                "sensor_measurement_18": 2388,
                "sensor_measurement_19": 100.0,
                "sensor_measurement_20": 39.08,
                "sensor_measurement_21": 23.4166
        },
        {
                "time_in_cycles": 4,
                "operational_setting_1": 0.0042,
                "operational_setting_2": 0.0,
                "operational_setting_3": 100.0,
                "sensor_measurement_1": 518.67,
                "sensor_measurement_2": 642.44,
                "sensor_measurement_3": 1584.12,
                "sensor_measurement_4": 1406.42,
                "sensor_measurement_5": 14.62,
                "sensor_measurement_6": 21.61,
                "sensor_measurement_7": 554.07,
                "sensor_measurement_8": 2388.03,
                "sensor_measurement_9": 9045.29,
                "sensor_measurement_10": 1.3,
                "sensor_measurement_11": 47.28,
                "sensor_measurement_12": 521.38,
                "sensor_measurement_13": 2388.05,
                "sensor_measurement_14": 8132.9,
                "sensor_measurement_15": 8.3917,
                "sensor_measurement_16": 0.03,
                "sensor_measurement_17": 391,
                "sensor_measurement_18": 2388,
                "sensor_measurement_19": 100.0,
                "sensor_measurement_20": 39.0,
                "sensor_measurement_21": 23.3737
        },
        {
                "time_in_cycles": 5,
                "operational_setting_1": 0.0014,
                "operational_setting_2": 0.0,
                "operational_setting_3": 100.0,
                "sensor_measurement_1": 518.67,
                "sensor_measurement_2": 642.51,
                "sensor_measurement_3": 1587.19,
                "sensor_measurement_4": 1401.92,
                "sensor_measurement_5": 14.62,
                "sensor_measurement_6": 21.61,
                "sensor_measurement_7": 554.16,
                "sensor_measurement_8": 2388.01,
                "sensor_measurement_9": 9044.55,
                "sensor_measurement_10": 1.3,
                "sensor_measurement_11": 47.31,
                "sensor_measurement_12": 522.15,
                "sensor_measurement_13": 2388.03,
                "sensor_measurement_14": 8129.54,
                "sensor_measurement_15": 8.4031,
                "sensor_measurement_16": 0.03,
                "sensor_measurement_17": 390,
                "sensor_measurement_18": 2388,
                "sensor_measurement_19": 100.0,
                "sensor_measurement_20": 38.99,
                "sensor_measurement_21": 23.413
        },
        {
                "time_in_cycles": 6,
                "operational_setting_1": 0.0012,
                "operational_setting_2": 0.0003,
                "operational_setting_3": 100.0,
                "sensor_measurement_1": 518.67,
                "sensor_measurement_2": 642.11,
                "sensor_measurement_3": 1579.12,
                "sensor_measurement_4": 1395.13,
                "sensor_measurement_5": 14.62,
                "sensor_measurement_6": 21.61,
                "sensor_measurement_7": 554.22,
                "sensor_measurement_8": 2388.0,
                "sensor_measurement_9": 9050.96,
                "sensor_measurement_10": 1.3,
                "sensor_measurement_11": 47.26,
                "sensor_measurement_12": 521.92,
                "sensor_measurement_13": 2388.08,
                "sensor_measurement_14": 8127.46,
                "sensor_measurement_15": 8.4238,
                "sensor_measurement_16": 0.03,
                "sensor_measurement_17": 392,
                "sensor_measurement_18": 2388,
                "sensor_measurement_19": 100.0,
                "sensor_measurement_20": 38.91,
                "sensor_measurement_21": 23.3467
        },
        {
                "time_in_cycles": 7,
                "operational_setting_1": -0.0,
                "operational_setting_2": 0.0002,
                "operational_setting_3": 100.0,
                "sensor_measurement_1": 518.67,
                "sensor_measurement_2": 642.11,
                "sensor_measurement_3": 1583.34,
                "sensor_measurement_4": 1404.84,
                "sensor_measurement_5": 14.62,
                "sensor_measurement_6": 21.61,
                "sensor_measurement_7": 553.89,
                "sensor_measurement_8": 2388.05,
                "sensor_measurement_9": 9051.39,
                "sensor_measurement_10": 1.3,
                "sensor_measurement_11": 47.31,
                "sensor_measurement_12": 522.01,
                "sensor_measurement_13": 2388.06,
                "sensor_measurement_14": 8134.97,
                "sensor_measurement_15": 8.3914,
                "sensor_measurement_16": 0.03,
                "sensor_measurement_17": 391,
                "sensor_measurement_18": 2388,
                "sensor_measurement_19": 100.0,
                "sensor_measurement_20": 38.85,
                "sensor_measurement_21": 23.3952
        },
        {
                "time_in_cycles": 8,
                "operational_setting_1": 0.0006,
                "operational_setting_2": -0.0,
                "operational_setting_3": 100.0,
                "sensor_measurement_1": 518.67,
                "sensor_measurement_2": 642.54,
                "sensor_measurement_3": 1580.89,
                "sensor_measurement_4": 1400.89,
                "sensor_measurement_5": 14.62,
                "sensor_measurement_6": 21.61,
                "sensor_measurement_7": 553.59,
                "sensor_measurement_8": 2388.05,
                "sensor_measurement_9": 9052.86,
                "sensor_measurement_10": 1.3,
                "sensor_measurement_11": 47.21,
                "sensor_measurement_12": 522.09,
                "sensor_measurement_13": 2388.06,
                "sensor_measurement_14": 8125.93,
                "sensor_measurement_15": 8.4213,
                "sensor_measurement_16": 0.03,
                "sensor_measurement_17": 393,
                "sensor_measurement_18": 2388,
                "sensor_measurement_19": 100.0,
                "sensor_measurement_20": 39.05,
                "sensor_measurement_21": 23.3224
        }
]
    }


def test_rul_prediction_success(client, valid_rul_payload):
    response = client.post("/predict/rul", json=valid_rul_payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data['predicted_rul_cycles'], float)
    assert data['predicted_rul_cycles'] > 0
    assert isinstance(data['xgboost_prediction'], float)
    # predicted_rul_cycles is an ensemble average of XGBoost + LSTM when
    # both predictions succeed, so it legitimately differs from
    # xgboost_prediction alone -- only require it to be in the same
    # plausible range, not identical.
    assert abs(data['predicted_rul_cycles'] - data['xgboost_prediction']) < 50
    assert data['lstm_prediction'] is None or isinstance(data['lstm_prediction'], float)


def test_rul_prediction_invalid_payload(client):
    invalid_payload = {
        "sensor_history": [
            {
                "time_in_cycles": 1,
                "sensor_measurement_2": 0.0023
            }
        ]
    }
    response = client.post("/predict/rul", json=invalid_payload)
    assert response.status_code >= 400
    assert response.status_code < 500