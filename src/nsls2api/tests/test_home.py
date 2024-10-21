import pytest
from httpx import ASGITransport, AsyncClient

from nsls2api.main import app


@pytest.mark.anyio
async def test_healthy_endpoint():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/healthy")
    assert response.status_code == 200
    assert response.text == "OK"
