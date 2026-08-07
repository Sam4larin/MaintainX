from pydantic import BaseModel
from typing import Any


class Asset(BaseModel):
    id: str
    name: str
    type: str
    risk_level: str
    maintenance_days: int
    details: dict[str, Any] | None = None


class AssetDetail(Asset):
    history: list[dict[str, Any]]
