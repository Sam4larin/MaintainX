from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_assets_endpoint(client):
    response = client.get('/assets')
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_missing_asset_returns_404(client):
    response = client.get('/assets/unknown-asset')
    assert response.status_code == 404
