from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_failure_risk_prediction_endpoint(client):
    payload = {
        'Air_temperature_K': 298.2,
        'Process_temperature_K': 308.7,
        'Rotational_speed_rpm': 1551,
        'Torque_Nm': 42.8,
        'Tool_wear_min': 0,
        'Type': 0,
        'temp_diff': 10.5,
        'power': 66400,
    }
    response = client.post('/predict/failure-risk', json=payload)
    assert response.status_code == 200
    assert 'failure_probability' in response.json()


def test_bad_payload_returns_422(client):
    response = client.post('/predict/failure-risk', json={'bad': 'payload'})
    assert response.status_code == 422