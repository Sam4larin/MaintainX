from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.routers.assets import router as assets_router
from backend.app.routers.health import router as health_router
from backend.app.routers.predictions import router as predictions_router
from backend.app.routers.upload import router as upload_router
from backend.app.services.model_loader import loader

logger = logging.getLogger('maintainx')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML artifacts at startup, but never let a missing/corrupt artifact
    # take the whole API down. Historically this raised straight out of
    # lifespan, which meant uvicorn exited before binding a port at all --
    # so every frontend request failed with a generic "Failed to fetch"
    # network error instead of a useful message. Now /health reports the
    # real problem (see routers/health.py) and every other endpoint that
    # actually needs a model returns a clear 503 instead of the process
    # never starting.
    try:
        loader.load()
    except Exception as exc:  # noqa: BLE001
        logger.error(
            'ML artifacts failed to load: %s. The API will still start, but every '
            '/predict/* endpoint will return 503 until this is fixed. Run '
            '`python -m ml.pipeline.train_all` to generate artifacts, or check '
            'ARTIFACTS_PATH in your .env.',
            exc,
        )
    yield


app = FastAPI(title='MaintainX API', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(health_router)
app.include_router(assets_router)
app.include_router(predictions_router)
app.include_router(upload_router)


@app.get('/')
def root():
    return {
        'service': 'MaintainX API',
        'docs': '/docs',
        'health': '/health',
    }
