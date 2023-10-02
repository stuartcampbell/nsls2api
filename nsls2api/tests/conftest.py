import pytest
from fastapi.testclient import TestClient

from nsls2api.main import api


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(api)
    yield client
