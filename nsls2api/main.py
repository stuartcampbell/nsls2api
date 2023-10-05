from pathlib import Path
from typing import Annotated

import fastapi
import uvicorn
from fastapi import Depends
from starlette.staticfiles import StaticFiles

from nsls2api.api.v1 import admin_api as admin_api_v1
from nsls2api.api.v1 import beamline_api as beamline_api_v1
from nsls2api.api.v1 import facility_api as facility_api_v1
from nsls2api.api.v1 import proposal_api as proposal_api_v1
from nsls2api.api.v1 import stats_api as stats_api_v1
from nsls2api.api.v1 import user_api as user_api_v1
from nsls2api.infrastructure import config
from nsls2api.infrastructure import mongodb_setup
from nsls2api.infrastructure.config import get_settings
from nsls2api.views import diagnostics
from nsls2api.views import home

settings = get_settings()

api = fastapi.FastAPI(
    title="NSLS-II API",
)

current_file = Path(__file__)
current_file_dir = current_file.parent
current_file_dir_absolute = current_file_dir.absolute()
project_root = current_file_dir.parent
project_root_absolute = project_root.resolve()
# static_root_absolute = project_root_absolute / "static"
static_root_absolute = current_file_dir_absolute / "static"


def main():
    configure_routing()
    uvicorn.run(api, port=8081)


def configure_routing():
    api.include_router(proposal_api_v1.router, prefix="/v1", tags=['proposal'])
    api.include_router(stats_api_v1.router, prefix="/v1")
    api.include_router(beamline_api_v1.router, prefix="/v1", tags=['beamline'])
    api.include_router(facility_api_v1.router, prefix="/v1", tags=['facility'])
    api.include_router(user_api_v1.router, prefix="/v1", tags=['user'])
    api.include_router(admin_api_v1.router, prefix="/v1", tags=['admin'])

    # Add this for backwards compatibility (for now)
    api.include_router(proposal_api_v1.router, include_in_schema=False)

    import subprocess
    cmd = "pwd"
    output = subprocess.run(cmd, shell=True)
    print(f"Current working directory: {output}")

    # Also include our webpages
    api.include_router(home.router)
    api.include_router(diagnostics.router)
    api.mount("/static", StaticFiles(directory=static_root_absolute), name="static")
    api.mount("/assets", StaticFiles(directory=static_root_absolute / "assets"), name="assets")


@api.get("/info", include_in_schema=False)
async def info(settings: Annotated[config.Settings, Depends(config.get_settings)]):
    return settings


@api.on_event("startup")
async def configure_db():
    await mongodb_setup.init_connection(settings.mongodb_dsn.unicode_string())
    # await mongodb_setup.init_connection("mongodb://localhost:27017/nsls2core-test")



if __name__ == "__main__":
    main()
else:
    configure_routing()
