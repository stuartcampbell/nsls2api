import fastapi

from nsls2api.api.models.facility_model import FacilityName
from nsls2api.services import proposal_service, facility_service

router = fastapi.APIRouter()


# TODO: Add back into schema when implemented.
@router.get(
    "/facility/{facility}/cycles/current", response_model=str, include_in_schema=False
)
async def get_current_facilty_cycle(facility: FacilityName):
    return "2024-1"

@router.get("/facility/{facility}/cycles", include_in_schema=True)
async def get_facility_cycles(facility: FacilityName):
    cycle_list = await facility_service.facility_cycles(facility.name)
    if cycle_list is None:
        return fastapi.responses.JSONResponse(
            {"error": f"No cycles were found for facility {facility.name}"},
            status_code=404,
        )
    data = {"facility": facility.name, "cycles": cycle_list}
    return data

@router.get("/facility/{facility}/cycle/{cycle}/proposals", include_in_schema=True)
async def get_proposals_for_cycle(facility: FacilityName, cycle: str):
    if facility.name != "nsls2":
        # TODO: Add other facilities
        return fastapi.responses.JSONResponse(
            {"message": f"Not implemented for the {facility.name} facility."},
            status_code=501,
        )

    proposal_list = await proposal_service.fetch_proposals_for_cycle(cycle)
    if proposal_list is None:
        return fastapi.responses.JSONResponse(
            {"error": f"No proposals were found for cycle {cycle}"},
            status_code=404,
        )
    data = {"cycle": cycle, "proposals": proposal_list}
    return data
