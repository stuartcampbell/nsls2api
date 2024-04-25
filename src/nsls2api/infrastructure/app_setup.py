import asyncio
from contextlib import asynccontextmanager

from nsls2api.infrastructure import mongodb_setup
from nsls2api.infrastructure.config import get_settings
from nsls2api.services import background_service
from nsls2api.services.helpers import HTTPXClientWrapper

settings = get_settings()
httpx_client_wrapper = HTTPXClientWrapper()

development_mode = True


@asynccontextmanager
async def app_lifespan(_):
    if development_mode:
        # Default to local mongodb with default port
        # and no authentication for development.
        # TODO: Refactor to use a different database for development.
        await mongodb_setup.init_connection(settings.mongodb_dsn.unicode_string())
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
