from fastapi import APIRouter

from backend.app.schemas.health import HealthResponse
from backend.app.services.model_loader import loader

router = APIRouter()


@router.get('/health', response_model=HealthResponse)
def health():
    if loader.artifacts:
        return {'status': 'ok', 'models_loaded': True, 'detail': None}
    return {
        'status': 'degraded',
        'models_loaded': False,
        'detail': (
            'ML artifacts are not loaded. Run `python -m ml.pipeline.train_all` to '
            'generate them, then restart the API, or check ARTIFACTS_PATH in .env.'
        ),
    }
