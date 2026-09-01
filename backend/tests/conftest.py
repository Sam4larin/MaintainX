import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope='session')
def client():
    """A TestClient that actually triggers FastAPI's lifespan startup event.

    TestClient(app) on its own does NOT run lifespan (which is what loads
    the ML models via loader.load()) unless used as a context manager.
    Every test file previously created `client = TestClient(app)` at
    module level, so every test ran against an app whose models were
    never loaded -- /health correctly reported 'degraded', and every
    /predict/* endpoint correctly returned 503, but that's not what any
    of these tests were meant to check.
    """
    with TestClient(app) as test_client:
        yield test_client
