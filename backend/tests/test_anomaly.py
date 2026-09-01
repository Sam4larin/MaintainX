import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


@pytest.fixture
def valid_anomaly_payload():
    return {
        "Air_temperature_K": 298.1,
        "Process_temperature_K": 308.6,
        "Rotational_speed_rpm": 1551,
        "Torque_Nm": 42.8,
        "Tool_wear_min": 0,
        "Type": 1,
        "temp_diff": 10.5,
        "power": 66382.8
    }

@pytest.fixture
def different_anomaly_payload():
    return {
        "Air_temperature_K": 300,
        "Process_temperature_K": 310,
        "Rotational_speed_rpm": 1600,
        "Torque_Nm": 45,
        "Tool_wear_min": 5,
        "Type": 2,
        "temp_diff": 10,
        "power": 70000
    }


def test_anomaly_prediction_success(client, valid_anomaly_payload):
    response = client.post("/predict/anomaly", json=valid_anomaly_payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data['is_anomaly'], bool)
    assert isinstance(data['isolation_forest_score'], float)
    assert isinstance(data['autoencoder_reconstruction_error'], float)
    assert data['autoencoder_reconstruction_error'] != data['isolation_forest_score'] * 0.5  # arbitrary ratio check


def test_anomaly_prediction_different_payloads(client, valid_anomaly_payload, different_anomaly_payload):
    response1 = client.post("/predict/anomaly", json=valid_anomaly_payload)
    response2 = client.post("/predict/anomaly", json=different_anomaly_payload)
    data1 = response1.json()
    data2 = response2.json()
    assert data1['autoencoder_reconstruction_error'] != data2['autoencoder_reconstruction_error'] * 0.5