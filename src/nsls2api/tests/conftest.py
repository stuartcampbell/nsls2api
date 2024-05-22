import beanie
import pytest
import motor.motor_asyncio

from nsls2api import models

@pytest.fixture(autouse=True)
async def init_connection():
    client = motor.motor_asyncio.AsyncIOMotorClient()
    await beanie.init_beanie(
        database=client.get_default_database(),
        document_models=models.all_models,
    )
    yield
    await client.close()