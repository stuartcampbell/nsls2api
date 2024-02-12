import fastapi
from fastapi import HTTPException, Depends
from fastapi.security.api_key import APIKey
from nsls2api.api.models.proposal_model import (
    ProposalDirectoriesList,
)

from nsls2api.infrastructure.logging import logger
from nsls2api.infrastructure.security import get_api_key, validate_admin_role
from nsls2api.models.beamlines import Beamline, BeamlineService, DetectorList
from nsls2api.services import beamline_service

router = fastapi.APIRouter()


@router.get("/beamline/{name}", response_model=Beamline)
async def details(name: str):
    beamline = await beamline_service.beamline_by_name(name)
    if beamline is None:
        raise HTTPException(
            status_code=451, detail=f"Beamline named {name} could not be found"
        )
    return beamline


# TODO: Add back into schema when we fully decide on the data model for the beamline services.
@router.get(
    "/beamline/{name}/services",
    response_model=list[BeamlineService],
    include_in_schema=False,
)
async def get_beamline_services(name: str):
    beamline_services = await beamline_service.all_services(name)
    if beamline_services is None:
        raise HTTPException(
            status_code=404, detail=f"Beamline named {name} could not be found"
        )
    return beamline_services


@router.get("/beamline/{name}/service-accounts")
async def get_beamline_accounts(name: str, api_key: APIKey = Depends(get_api_key)):
    service_accounts = await beamline_service.service_accounts(name)
    if service_accounts is None:
        raise HTTPException(
            status_code=404, detail=f"Beamline named {name} could not be found"
        )
    return service_accounts


@router.get(
    "/beamline/{name}/detectors", response_model=DetectorList, include_in_schema=True
)
async def get_beamline_detectors(name: str) -> DetectorList:
    detectors = await beamline_service.detectors(name)
    if detectors is None:
        raise HTTPException(
            status_code=404,
            detail=f"No detectors for the {name} beamline could not be found.",
        )

    response_model = DetectorList(detectors=detectors, count=len(detectors))
    return response_model


@router.get(
    "/beamline/{name}/proposal-directory-skeleton",
    response_model=ProposalDirectoriesList,
)
async def get_beamline_proposal_directory_skeleton(name: str):
    directory_skeleton = await beamline_service.proposal_directory_skeleton(name)
    if directory_skeleton is None:
        raise HTTPException(
            status_code=404,
            detail=f"No proposal directory skeleton for the {name} beamline could be generated.",
        )
    response_model = ProposalDirectoriesList(
        directory_count=len(directory_skeleton), directories=directory_skeleton
    )
    return response_model


@router.get(
    "/beamline/{name}/proposal-directory-skeleton-alternate",
    response_model=ProposalDirectoriesList,
    include_in_schema=False,
)
async def get_beamline_proposal_directory_skeleton_alternate(
    name: str, proposal_id: int
):
    directory_skeleton = await beamline_service.proposal_directory_skeleton(name)
    if directory_skeleton is None:
        raise HTTPException(
            status_code=404,
            detail=f"No proposal directory skeleton for the {name} beamline could be generated.",
        )
    response_model = ProposalDirectoriesList(
        directory_count=len(directory_skeleton), directories=directory_skeleton
    )
    return response_model


# TODO: Review if we want to also have the following endpoints for the beamline accounts or
#       if we want to have a single endpoint (above) that returns all the accounts for a beamline.


@router.get(
    "/beamline/{name}/accounts/workflow", response_model=str, include_in_schema=False
)
async def get_beamline_workflow_username(name: str):
    workflow_user = await beamline_service.workflow_username(name)
    if workflow_user is None:
        raise HTTPException(
            status_code=404,
            detail=f"No workflow user has been defined for the {name} beamline",
        )
    return workflow_user


@router.get(
    "/beamline/{name}/accounts/ioc", response_model=str, include_in_schema=False
)
async def get_beamline_ioc_username(name: str):
    ioc_user = await beamline_service.ioc_username(name)
    if ioc_user is None:
        raise HTTPException(
            status_code=404,
            detail=f"No IOC user has been defined for the {name} beamline",
        )
    return ioc_user


@router.get(
    "/beamline/{name}/accounts/bluesky", response_model=str, include_in_schema=False
)
async def get_beamline_bluesky_username(name: str):
    bluesky_user = await beamline_service.bluesky_username(name)
    if bluesky_user is None:
        raise HTTPException(
            status_code=404,
            detail=f"No bluesky user has been defined for the {name} beamline",
        )
    return bluesky_user


@router.get(
    "/beamline/{name}/accounts/epics-services",
    response_model=str,
    include_in_schema=False,
)
async def get_beamline_epics_services_username(name: str):
    epics_user = await beamline_service.epics_services_username(name)
    if epics_user is None:
        raise HTTPException(
            status_code=404,
            detail=f"No EPICS services user has been defined for the {name} beamline",
        )
    return epics_user


@router.get(
    "/beamline/{name}/accounts/operator", response_model=str, include_in_schema=False
)
async def get_beamline_operator_username(name: str):
    operator_user = await beamline_service.operator_username(name)
    if operator_user is None:
        raise HTTPException(
            status_code=404,
            detail=f"No operator user has been defined for the {name} beamline",
        )
    return operator_user


@router.get("/beamline/{name}/services/", response_model=list[BeamlineService])
async def get_beamline_services(name: str):
    beamline_services = await beamline_service.all_services(name)
    if beamline_services is None:
        raise HTTPException(
            status_code=404, detail=f"Beamline named {name} could not be found"
        )
    return beamline_services


@router.put(
    "/beamline/{name}/services/",
    include_in_schema=True,
    response_model=BeamlineService,
    dependencies=[Depends(validate_admin_role)],
)
async def add_beamline_service(name: str, service: BeamlineService):
    logger.info(f"Adding service {service.name} to beamline {name}")

    new_service = await beamline_service.add_service(
        beamline_name=name,
        service_name=service.name,
        used_in_production=service.used_in_production,
        host=service.host,
        port=service.port,
        uri=service.uri,
    )

    if new_service is None:
        raise HTTPException(
            status_code=404,
            detail=f"Service {service.name} already exists in beamline {name}",
        )

    return new_service
