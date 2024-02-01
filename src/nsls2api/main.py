from pathlib import Path

import fastapi
import logging
import uvicorn

from asgi_correlation_id import CorrelationIdMiddleware

from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.staticfiles import StaticFiles

from nsls2api.api.v1 import admin_api as admin_api_v1
from nsls2api.api.v1 import beamline_api as beamline_api_v1
from nsls2api.api.v1 import facility_api as facility_api_v1
from nsls2api.api.v1 import proposal_api as proposal_api_v1
from nsls2api.api.v1 import stats_api as stats_api_v1
from nsls2api.api.v1 import user_api as user_api_v1
from nsls2api.infrastructure import mongodb_setup
from nsls2api.infrastructure.config import get_settings
from nsls2api.infrastructure.logging import configure_logging
from nsls2api.views import diagnostics
from nsls2api.views import home
from nsls2api.middleware import ProcessTimeMiddleware
from nsls2api.middleware import log_request
from fastapi.exceptions import RequestValidationError
from nsls2api.exception_handlers import request_validation_exception_handler, http_exception_handler, unhandled_exception_handler


settings = get_settings()

logger = logging.getLogger(__name__)

middleware = [Middleware(ProcessTimeMiddleware)]

app = fastapi.FastAPI(title="NSLS-II API", middleware=middleware, on_startup=[configure_logging])
app.add_middleware(CorrelationIdMiddleware)

app.middleware("http")(log_request)

app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


current_file = Path(__file__)
current_file_dir = current_file.parent
current_file_dir_absolute = current_file_dir.absolute()
project_root = current_file_dir.parent
project_root_absolute = project_root.resolve()
static_root_absolute = current_file_dir_absolute / "static"


def main():
    configure_routing()
    uvicorn.run(app, port=8081)


def configure_routing():
    logger.info("Configuring routing")
    app.include_router(proposal_api_v1.router, prefix="/v1", tags=["proposal"])
    app.include_router(stats_api_v1.router, prefix="/v1")
    app.include_router(beamline_api_v1.router, prefix="/v1", tags=["beamline"])
    app.include_router(facility_api_v1.router, prefix="/v1", tags=["facility"])
    app.include_router(user_api_v1.router, prefix="/v1", tags=["user"])
    app.include_router(admin_api_v1.router, prefix="/v1", tags=["admin"])

    # Add this for backwards compatibility (for now)
    app.include_router(proposal_api_v1.router, include_in_schema=False)

    import subprocess

    cmd = "pwd"
    output = subprocess.run(cmd, shell=True)
    print(f"Current working directory: {output}")

    # Also include our webpages
    app.include_router(home.router)
    app.include_router(diagnostics.router)
    app.mount("/static", StaticFiles(directory=static_root_absolute), name="static")
    app.mount(
        "/assets",
        StaticFiles(directory=static_root_absolute / "assets"),
        name="assets",
    )


@app.on_event("startup")
async def configure_db():
    await mongodb_setup.init_connection(settings.mongodb_dsn.unicode_string())


if __name__ == "__main__":
    main()
else:
    configure_routing()
