import fastapi
import uvicorn
from starlette.staticfiles import StaticFiles

from api import proposal_api, stats_api, facility_api, beamline_api
from views import home
from infrastructure import mongodb_setup

api = fastapi.FastAPI()


def main():
    configure_routing()
    uvicorn.run(api)


def configure_routing():
    api.include_router(proposal_api.router)
    api.include_router(stats_api.router)
    api.include_router(facility_api.router)
    api.include_router(beamline_api.router)

    # Also include our webpages
    api.include_router(home.router)
    api.mount('/static', StaticFiles(directory='static'), name='static')


@api.on_event('startup')
async def configure_db():
    await mongodb_setup.init_connection('nsls2core-test')


if __name__ == '__main__':
    main()
else:
    configure_routing()
