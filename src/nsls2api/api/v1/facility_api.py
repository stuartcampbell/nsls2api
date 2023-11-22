import fastapi

from nsls2api.api.models.facility_model import FacilityName

router = fastapi.APIRouter()


@router.get("/facility/{facility}/cycles/current", response_model=str)
async def get_current_facilty_cycle(facility: FacilityName):
    return "2023-3"
