from fastapi import APIRouter, HTTPException

from backend.app.schemas.prediction import AnomalyRequest, AnomalyResponse, FailureRiskRequest, FailureRiskResponse, ForecastRequest, ForecastResponse, RULRequest, RULResponse
from backend.app.services.anomaly_service import predict_anomaly
from backend.app.services.classification_service import predict_failure_risk
from backend.app.services.forecasting_service import forecast
from backend.app.services.regression_service import predict_rul

router = APIRouter()


@router.post('/predict/failure-risk', response_model=FailureRiskResponse)
def failure_risk(payload: FailureRiskRequest):
    return predict_failure_risk(payload.model_dump())


@router.post('/predict/rul', response_model=RULResponse)
def rul(payload: RULRequest):
    return predict_rul(payload.model_dump())


@router.post('/predict/anomaly', response_model=AnomalyResponse)
def anomaly(payload: AnomalyRequest):
    return predict_anomaly(payload.model_dump())


@router.post('/predict/forecast', response_model=ForecastResponse)
def forecast_endpoint(payload: ForecastRequest):
    return forecast(payload.model_dump())
