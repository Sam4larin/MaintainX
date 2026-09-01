from fastapi import APIRouter, HTTPException

from backend.app.schemas.prediction import AnomalyRequest, AnomalyResponse, FailureRiskRequest, FailureRiskResponse, ForecastRequest, ForecastResponse, RULRequest, RULResponse
from backend.app.services.anomaly_service import predict_anomaly
from backend.app.services.classification_service import predict_failure_risk
from backend.app.services.forecasting_service import forecast
from backend.app.services.regression_service import predict_rul

router = APIRouter()


@router.post('/predict/failure-risk', response_model=FailureRiskResponse)
def failure_risk(payload: FailureRiskRequest):
    try:
        return predict_failure_risk(payload.model_dump())
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/predict/rul', response_model=RULResponse)
def rul(payload: RULRequest):
    try:
        return predict_rul(payload.model_dump())
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/predict/anomaly', response_model=AnomalyResponse)
def anomaly(payload: AnomalyRequest):
    try:
        return predict_anomaly(payload.model_dump())
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/predict/forecast', response_model=ForecastResponse)
def forecast_endpoint(payload: ForecastRequest):
    try:
        return forecast(payload.model_dump())
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
