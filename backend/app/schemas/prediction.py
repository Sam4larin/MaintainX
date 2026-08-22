from pydantic import BaseModel
from typing import Any


class FailureRiskRequest(BaseModel):
    Air_temperature_K: float
    Process_temperature_K: float
    Rotational_speed_rpm: float
    Torque_Nm: float
    Tool_wear_min: float
    Type: int
    temp_diff: float
    power: float


class FailureRiskResponse(BaseModel):
    failure_probability: float
    risk_level: str
    failure_type_prediction: str
    failure_type_probabilities: dict[str, float]


class RULRequest(BaseModel):
    sensor_history: list[dict[str, Any]]


class RULResponse(BaseModel):
    predicted_rul_cycles: float
    predicted_rul_days: float
    recommended_maintenance_window_days: int
    model_used: str
    xgboost_prediction: float
    lstm_prediction: float | None = None


class AnomalyRequest(BaseModel):
    Air_temperature_K: float
    Process_temperature_K: float
    Rotational_speed_rpm: float
    Torque_Nm: float
    Tool_wear_min: float
    Type: int
    temp_diff: float
    power: float


class AnomalyResponse(BaseModel):
    is_anomaly: bool
    isolation_forest_score: float
    autoencoder_reconstruction_error: float
    anomaly_threshold: float


class ForecastRequest(BaseModel):
    sensor_history: list[dict[str, Any]]


class ForecastResponse(BaseModel):
    forecasted_cycles: list[int]
    forecasted_sensor_values: dict[str, list[float]]