from fastapi import APIRouter, HTTPException

from backend.app.schemas.asset import Asset, AssetDetail
from backend.app.services.asset_service import get_asset, load_assets

router = APIRouter()


@router.get('/assets', response_model=list[Asset])
def list_assets():
    return [Asset(**asset) for asset in load_assets()]


@router.get('/assets/{asset_id}', response_model=AssetDetail)
def get_asset_by_id(asset_id: str):
    asset = get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail='Asset not found')
    return AssetDetail(**asset)
