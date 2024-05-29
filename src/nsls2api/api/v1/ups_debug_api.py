import fastapi

from nsls2api.api.models.facility_model import UpsFacilityName
from nsls2api.models.proposal_types import ProposalType
from nsls2api.models.universalproposal_models import UpsProposalRecord, UpsProposalType, UpsRunCycleProposalMapping
from nsls2api.services import proposal_service, universalproposal_service

router = fastapi.APIRouter()

@router.get("/ups/raw/proposal_types")
async def get_ups_raw_proposal_types(facility: UpsFacilityName):
    proposal_types = await universalproposal_service.get_raw_proposal_types(facility=facility)
    return proposal_types

@router.get("/ups/proposal_types")
async def get_ups_proposal_types(facility: UpsFacilityName) -> list[ProposalType]:
    ups_proposal_types = await universalproposal_service.get_proposal_types(facility=facility)

    proposal_types = []
    for ups_proposal_type in ups_proposal_types:
        proposal_types.append(await proposal_service.convert_ups_proposal_type(ups_proposal_type))

    return proposal_types


@router.get("/ups/raw/cycles")
async def get_ups_raw_cycles(facility: UpsFacilityName):
    cycles = await universalproposal_service.get_cycles(facility=facility)
    return cycles

@router.get("/ups/cycles")
async def get_ups_cycles(facility: UpsFacilityName):
    cycles = await universalproposal_service.get_cycles(facility=facility)
    return cycles

@router.get("/ups/raw/facility_info/")
async def get_ups_facility_info(facility_name: UpsFacilityName = None):

    if facility_name is None:
        facility_info = await universalproposal_service.get_all_facility_details()
    else:
        facility_info = await universalproposal_service.get_facility_details(facility=facility_name)
    
    return facility_info


@router.get("/ups/raw/proposal/{proposal_id}")
async def get_ups_raw_proposal(proposal_id: str):
    """
    Retrieves the raw proposal_record from UPS for a given proposal ID.

    Args:
        proposal_id (str): The ID of the proposal to retrieve.

    Returns:
        The response from the Service Now Table API for the 'sn_customerservice_proposal_record' table
    """
    proposal = await universalproposal_service.get_raw_proposal(proposal_id=proposal_id)
    return proposal

@router.get("/ups/proposal/{proposal_id}")
async def get_ups_proposal(proposal_id: str) -> UpsProposalRecord:
    
    try:
        proposal = await universalproposal_service.get_proposal(proposal_id=proposal_id)
        if proposal is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=f"Proposal {proposal_id} not found", 
        )
    except LookupError as e:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=e.args[0], 
        )
    # response_model = SingleProposal(proposal=proposal)
    return proposal

@router.get("/ups/proposals/cycle/{cycle_name}")
async def get_ups_cycle_proposal_mapping(cycle_name: str, facility: UpsFacilityName):
    cycle_list = await universalproposal_service.get_proposals_for_cycle(cycle_name=cycle_name, facility=facility)

    return cycle_list

@router.get("/ups/proposals/")
async def get_ups_all_proposals(facility: UpsFacilityName):
    proposals = await universalproposal_service.get_all_proposals_for_facility(facility=facility)
    # try:
    #     proposals = await universalproposal_service.get_all_proposals_for_facility(facility=facility)
    #     if proposals is None:
    #         raise fastapi.HTTPException(
    #             status_code=fastapi.status.HTTP_404_NOT_FOUND,
    #             detail=f"No Proposals for {facility} were found", 
    #     )
    # except LookupError as e:
    #         raise fastapi.HTTPException(
    #             status_code=fastapi.status.HTTP_404_NOT_FOUND,
    #             detail=e.args[0], 
    #     )
    # response_model = SingleProposal(proposal=proposal)

    data = {"counts":len(proposals), "proposals": proposals}

    return data