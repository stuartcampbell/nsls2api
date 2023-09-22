from typing import Annotated

import fastapi
import uvicorn
from fastapi import Depends
from starlette.staticfiles import StaticFiles

from infrastructure import mongodb_setup
from nsls2api.api.v1 import beamline_api as beamline_api_v1
from nsls2api.api.v1 import facility_api as facility_api_v1
from nsls2api.api.v1 import proposal_api as proposal_api_v1
from nsls2api.api.v1 import stats_api as stats_api_v1
from nsls2api.api.v1 import user_api as user_api_v1
from nsls2api.infrastructure import config
from nsls2api.views import diagnostics
from nsls2api.views import home

api = fastapi.FastAPI()


def main():
    configure_routing()
    uvicorn.run(api, port=8081)

    settings = config.get_settings()
    print(settings)


def configure_routing():
    api.include_router(proposal_api_v1.router, prefix="/v1")
    api.include_router(stats_api_v1.router, prefix="/v1")
    api.include_router(beamline_api_v1.router, prefix="/v1")
    api.include_router(facility_api_v1.router, prefix="/v1")
    api.include_router(user_api_v1.router, prefix="/v1")

    # Add this for backwards compatibility (for now)
    api.include_router(proposal_api_v1.router, include_in_schema=False)

    # Also include our webpages
    api.include_router(home.router)
    api.include_router(diagnostics.router)
    api.mount("/static", StaticFiles(directory="static"), name="static")
    api.mount("/assets", StaticFiles(directory="static/assets"), name="assets")


@api.get("/info", include_in_schema=False)
async def info(settings: Annotated[config.Settings, Depends(config.get_settings)]):
    return settings


@api.on_event("startup")
async def configure_db():
    await mongodb_setup.init_connection("localhost", 27017, "nsls2core-test")


if __name__ == "__main__":
    main()
else:
    configure_routing()
