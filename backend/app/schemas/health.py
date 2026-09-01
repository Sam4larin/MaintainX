from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool = True
    detail: str | None = None
