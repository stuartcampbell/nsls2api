import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

from nsls2api.main import app


@pytest_asyncio.fixture(scope="function", autouse=True, loop_scope="function")
async def test_client(db):
    async with LifespanManager(app, startup_timeout=100, shutdown_timeout=100):
        server_name = "http://localhost"
        async with AsyncClient(transport=ASGITransport(app=app), base_url=server_name, follow_redirects=True) as client:
            yield client
