import fastapi

from nsls2api.api.models.beamline_model import BeamlineServicesModel
# from nsls2api.api.models.beamline_model import BeamlineResponseModel
from nsls2api.models.beamlines import Beamline, BeamlineService
from nsls2api.services import beamline_service

router = fastapi.APIRouter()


@router.get('/beamline/{name}', response_model=Beamline)
async def details(name: str):
    beamline = await beamline_service.beamline_by_name(name)
    if beamline is None:
        return fastapi.responses.JSONResponse({'error': f'Beamline named {name} could not be found'},
                                              status_code=404)
    return beamline

@router.get('/beamline/{name}/services', response_model=BeamlineServicesModel)
async def get_beamline_services(name: str):
    beamline_services = await beamline_service.all_services(name)
    if beamline_services is None:
        return fastapi.responses.JSONResponse({'error': f'Beamline named {name} could not be found'},
                                              status_code=404)

    service_list = BeamlineServicesModel(count=2, services=*beamline_services)

    return service_list
