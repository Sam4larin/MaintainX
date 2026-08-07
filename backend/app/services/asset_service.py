import json
from pathlib import Path

from backend.app.config import settings

ROOT = Path(__file__).resolve().parents[3]
DATA_FILE = ROOT / 'backend' / 'app' / 'data' / 'demo_assets.json'


def load_assets() -> list[dict]:
    return json.loads(DATA_FILE.read_text(encoding='utf-8'))


def get_asset(asset_id: str) -> dict | None:
    assets = load_assets()
    return next((a for a in assets if a['id'] == asset_id), None)
