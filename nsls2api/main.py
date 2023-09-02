import fastapi
import uvicorn
from starlette.staticfiles import StaticFiles

from nsls2api.api.v1 import stats_api as stats_api_v1
from nsls2api.api.v1 import facility_api as facility_api_v1
from nsls2api.api.v1 import beamline_api as beamline_api_v1
from nsls2api.api.v1 import proposal_api as proposal_api_v1
from nsls2api.api.v1 import user_api as user_api_v1
from nsls2api.views import home
from infrastructure import mongodb_setup

api = fastapi.FastAPI()

def main():
    configure_routing()
    uvicorn.run(api, port=8080)


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
    api.mount('/static', StaticFiles(directory='static'), name='static')


@api.on_event('startup')
async def configure_db():
    await mongodb_setup.init_connection('localhost', 27017, 'nsls2core-test')


if __name__ == '__main__':
    main()
else:
    configure_routing()
