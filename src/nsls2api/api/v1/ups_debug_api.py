import fastapi

from nsls2api.api.models.facility_model import UpsFacilityName
from nsls2api.services import universalproposal_service

router = fastapi.APIRouter()

@router.get("/ups/proposal_types")
async def get_ups_proposal_types(facility: UpsFacilityName):
    proposal_types = await universalproposal_service.get_proposal_types(facility=facility)

    return proposal_types

@router.get("/ups/facility_info/{facility_name}")
async def get_ups_facility_info(facility_name: UpsFacilityName):
    facility_info = await universalproposal_service.get_facility_details(facility=facility_name)
    return facility_info