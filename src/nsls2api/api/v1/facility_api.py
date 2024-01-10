import fastapi

from nsls2api.api.models.facility_model import FacilityName

router = fastapi.APIRouter()

# TODO: Add back into schema when implemented.
@router.get("/facility/{facility}/cycles/current", response_model=str, include_in_schema=False)
async def get_current_facilty_cycle(facility: FacilityName):
    return "2023-3"
