from pydantic import BaseModel
from typing import Any, Literal


class ParsedAi4iRow(BaseModel):
    """One row shaped for /predict/failure-risk and /predict/anomaly."""

    Air_temperature_K: float
    Process_temperature_K: float
    Rotational_speed_rpm: float
    Torque_Nm: float
    Tool_wear_min: float
    Type: int
    temp_diff: float
    power: float
    source_row: int


class UploadParseResponse(BaseModel):
    detected_format: Literal['ai4i', 'cmapss', 'unknown']
    row_count: int
    warnings: list[str] = []
    ai4i_rows: list[ParsedAi4iRow] = []
    sensor_history: list[dict[str, Any]] = []
    columns_found: list[str] = []
