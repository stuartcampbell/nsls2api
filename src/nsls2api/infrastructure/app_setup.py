import asyncio
from contextlib import asynccontextmanager

from nsls2api.infrastructure import mongodb_setup
from nsls2api.infrastructure.config import get_settings
from nsls2api.services import background_service
from nsls2api.services.helpers import HTTPXClientWrapper

settings = get_settings()
httpx_client_wrapper = HTTPXClientWrapper()

local_development_mode = False


@asynccontextmanager
async def app_lifespan(_):
    if local_development_mode:
        # Default to local mongodb with default port
        # and no authentication for development.
        development_dsn = mongodb_setup.create_connection_string(
            host="localhost", port=27017, db_name="nsls2core-development"
        )
        await mongodb_setup.init_connection(development_dsn.unicode_string())
    else:
        await mongodb_setup.init_connection(settings.mongodb_dsn.unicode_string())

    # Create a shared httpx client
    httpx_client_wrapper.start()

    # Start the background workers

    # noinspection PyAsyncCall
    asyncio.create_task(background_service.worker_function())

    yield

    # Cleanup httpx client
    await httpx_client_wrapper.stop()
