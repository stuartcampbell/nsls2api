import fastapi

from nsls2api.api.models.facility_model import UpsFacilityName
from nsls2api.services import universalproposal_service

router = fastapi.APIRouter()

@router.get("/ups/raw/proposal_types")
async def get_ups_proposal_types(facility: UpsFacilityName):
    proposal_types = await universalproposal_service.get_proposal_types(facility=facility)

    return proposal_types

@router.get("/ups/raw/facility_info/")
async def get_ups_facility_info(facility_name: UpsFacilityName = None):

    if facility_name is None:
        facility_info = await universalproposal_service.get_all_facility_details()
    else:
        facility_info = await universalproposal_service.get_facility_details(facility=facility_name)
    
    return facility_info


@router.get("/ups/raw/proposal/{proposal_id}")
async def get_ups_proposal(proposal_id: str):
    proposal = await universalproposal_service.get_raw_proposal(proposal_id=proposal_id)
    return proposal

