import fastapi

from fastapi import HTTPException
from nsls2api.api.models.beamline_model import BeamlineServicesModel
from nsls2api.models.beamlines import Beamline, BeamlineService
from nsls2api.services import beamline_service

router = fastapi.APIRouter()


@router.get('/beamline/{name}', response_model=Beamline)
async def details(name: str):
    beamline = await beamline_service.beamline_by_name(name)
    if beamline is None:
        raise HTTPException(status_code=404, detail=f'Beamline named {name} could not be found')
    return beamline

@router.get('/beamline/{name}/services', response_model=list[BeamlineService])
async def get_beamline_services(name: str):
    beamline_services = await beamline_service.all_services(name)
    if beamline_services is None:
        raise HTTPException(status_code=404, detail=f'Beamline named {name} could not be found')

    # service_list = BeamlineServicesModel(count=2, services=beamline_services)

    return beamline_services


@router.get('/beamline/{name}/accounts/workflow')
async def get_beamline_workflow_username(name: str):
    workflow_user = await beamline_service.workflow_username(name)
    if workflow_user is None:
        raise HTTPException(status_code=404, detail=f'No workflow user has been defined for the {name} beamline')