from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.routers.assets import router as assets_router
from backend.app.routers.health import router as health_router
from backend.app.routers.predictions import router as predictions_router
from backend.app.services.model_loader import loader


@asynccontextmanager
async def lifespan(app: FastAPI):
    loader.load()
    yield


app = FastAPI(title='MaintainX API', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(health_router)
app.include_router(assets_router)
app.include_router(predictions_router)
