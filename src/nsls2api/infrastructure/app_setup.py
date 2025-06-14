import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from nsls2api.infrastructure import mongodb_setup
from nsls2api.infrastructure.config import get_settings
from nsls2api.infrastructure.logging import logger
from nsls2api.services import background_service
from nsls2api.services.helpers import httpx_client_wrapper
from nsls2api.version import get_version

settings = get_settings()

local_development_mode = False


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Log the version of the nsls2api package
    logger.info(f"NSLS-II API Version: {get_version()}")

    # Initialize the MongoDB connection
    await mongodb_setup.init_connection(settings.mongodb_dsn)

    # Create a shared httpx client
    httpx_client_wrapper.start()

    # Start the background workers

    # noinspection PyAsyncCall
    asyncio.create_task(background_service.worker_function())

    yield

    # Cleanup httpx client
    await httpx_client_wrapper.stop()
