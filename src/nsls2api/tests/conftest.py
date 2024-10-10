import asyncio

import pytest
from pydantic import MongoDsn
from pydantic_settings import BaseSettings

from nsls2api.infrastructure.mongodb_setup import create_connection_string, init_connection

@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()

@pytest.fixture(scope="session", autouse=True)
async def db():
    mongodb_dsn = create_connection_string(host="localhost", port=27017, db_name="test_db")
    await init_connection(mongodb_dsn.unicode_string())
    # client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)
    # print(f'client: {client[settings.mongodb_db_name]}')
    # return client[settings.mongodb_db_name]
