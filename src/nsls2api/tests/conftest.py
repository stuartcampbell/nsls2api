import motor.motor_asyncio
import pytest
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27017/test_db"
    mongodb_db_name: str = "test_db"


@pytest.fixture
def settings():
    return Settings()

@pytest.fixture
def db(settings: Settings) -> motor.motor_asyncio.AsyncIOMotorDatabase:
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)
    print(f'client: {client[settings.mongodb_db_name]}')
    return client[settings.mongodb_db_name]
