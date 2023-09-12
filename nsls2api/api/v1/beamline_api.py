import fastapi

from fastapi import HTTPException, Depends
from fastapi.security.api_key import APIKey
from nsls2api.infrastructure.security import get_api_key

from nsls2api.infrastructure.security import get_api_key
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
    return beamline_services

@router.get('/beamline/{name}/accounts')
async def get_beamline_accounts(name: str, api_key: APIKey = Depends(get_api_key)):
    service_accounts = await beamline_service.beamline_service_accounts(name)
    if service_accounts is None:
        raise HTTPException(status_code=404, detail=f"Beamline named {name} could not be found")
    return service_accounts


@router.get('/beamline/{name}/accounts/workflow',response_model=str)
async def get_beamline_workflow_username(name: str):
    workflow_user = await beamline_service.workflow_username(name)
    if workflow_user is None:
        raise HTTPException(status_code=404, detail=f'No workflow user has been defined for the {name} beamline')
    return workflow_user

@router.get('/beamline/{name}/accounts/ioc',response_model=str)
async def get_beamline_ioc_username(name: str):
    ioc_user = await beamline_service.ioc_username(name)
    if ioc_user is None:
        raise HTTPException(status_code=404, detail=f'No IOC user has been defined for the {name} beamline')
    return ioc_user

@router.get('/beamline/{name}/accounts/bluesky',response_model=str)
async def get_beamline_bluesky_username(name: str):
    bluesky_user = await beamline_service.bluesky_username(name)
    if bluesky_user is None:
        raise HTTPException(status_code=404, detail=f'No bluesky user has been defined for the {name} beamline')
    return bluesky_user

@router.get('/beamline/{name}/accounts/epics-services',response_model=str)
async def get_beamline_epics_services_username(name: str):
    epics_user = await beamline_service.epics_services_username(name)
    if epics_user is None:
        raise HTTPException(status_code=404, detail=f'No EPICS services user has been defined for the {name} beamline')
    return epics_user

@router.get('/beamline/{name}/accounts/operator',response_model=str)
async def get_beamline_operator_username(name: str):
    operator_user = await beamline_service.operator_username(name)
    if operator_user is None:
        raise HTTPException(status_code=404, detail=f'No operator user has been defined for the {name} beamline')
    return operator_user
