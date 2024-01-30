from typing import Annotated, List, Optional
import fastapi
from fastapi import Depends, HTTPException, Query

from nsls2api.api.models.proposal_model import (
    CommissioningProposalsModel,
    RecentProposal,
    RecentProposalsModel,
)
from nsls2api.api.models.proposal_model import UsernamesModel, ProposalDirectories
from nsls2api.infrastructure.security import get_current_user
from nsls2api.models.proposals import Proposal, User
from nsls2api.services import proposal_service
from nsls2api.api.models.facility_model import FacilityName


router = fastapi.APIRouter()


@router.get("/proposals/recent/{count}", response_model=RecentProposalsModel)
async def get_recent_proposals(count: int, beamline: str | None = None):
    count = max(1, count)
    proposals = await proposal_service.recently_updated(count, beamline=beamline)

    proposal_models = [
        RecentProposal(
            proposal_id=p.proposal_id,
            title=p.title,
            updated=p.last_updated,
            instruments=p.instruments,
        )
        for p in proposals
    ]
    model = RecentProposalsModel(count=count, proposals=proposal_models)

    return model


@router.get("/proposals/commissioning", response_model=CommissioningProposalsModel)
async def get_commissioning_proposals(beamline: str | None = None):
    proposals = await proposal_service.commissioning_proposals(beamline=beamline)
    if proposals is None:
        return fastapi.responses.JSONResponse(
            {"error": "Commissioning Proposals not found"}, status_code=404
        )
    model = CommissioningProposalsModel(
        count=len(proposals), commissioning_proposals=proposals
    )
    return model


# TODO: Add back into schema when implemented.
@router.get("/proposals/", include_in_schema=True)
async def get_proposals(
    proposal_id: Annotated[list[str] | None, Query()] = None,
    beamline: Annotated[list[str] | None, Query()] = None,
    cycle: Annotated[list[str] | None, Query()] = None,
    page_size: int = 10,
    page: int = 1,
):
    proposal_list = await proposal_service.fetch_proposals(
        proposal_id=proposal_id,
        beamline=beamline,
        cycle=cycle,
        page_size=page_size,
        page=page,
    )
    return proposal_list


@router.get("/proposal/{proposal_id}", response_model=Proposal)
async def get_proposal(proposal_id: int, beamline: str | None = None):
    proposal = await proposal_service.proposal_by_id(proposal_id)
    if proposal is None:
        return fastapi.responses.JSONResponse(
            {"error": f"Proposal {proposal_id} not found"}, status_code=404
        )
    return proposal


# TODO: Add back into schema when implemented.
@router.post(
    "/proposal/{proposal_id}",
    response_model=Proposal,
    dependencies=[Depends(get_current_user)],
    include_in_schema=False,
)
async def create_proposal(proposal_id: int) -> Proposal:
    proposal = await proposal_service.create_proposal(proposal_id)
    if proposal is None:
        raise HTTPException(
            status_code=404, detail=f"Failed to create proposal {proposal_id}."
        )
    return proposal


@router.get("/proposal/{proposal_id}/users", response_model=list[User])
async def get_proposals_users(proposal_id: int):
    users = await proposal_service.fetch_users_on_proposal(proposal_id)
    return users


@router.get("/proposal/{proposal_id}/principal-investigator", response_model=list[User])
async def get_proposal_principle_invesigator(proposal_id: int):
    principle_invesigator = await proposal_service.pi_from_proposal(proposal_id)

    if len(principle_invesigator) == 0:
        return fastapi.responses.JSONResponse(
            {"error": f"PI not found for proposal {proposal_id}"},
            status_code=404,
        )
    elif len(principle_invesigator) > 1:
        return fastapi.responses.JSONResponse(
            {"error": f"Proposal {proposal_id} contains more than one PI"},
            status_code=422,
        )

    return principle_invesigator


@router.get("/proposal/{proposal_id}/usernames", response_model=UsernamesModel)
async def get_proposal_usernames(proposal_id: int):
    # Check to see if proposal exists
    if not await proposal_service.exists(proposal_id):
        return fastapi.responses.JSONResponse(
            {"error": f"Proposal {proposal_id} not found"}, status_code=404
        )

    proposal_usernames = await proposal_service.fetch_usernames_from_proposal(
        proposal_id
    )
    model = UsernamesModel(usernames=proposal_usernames)

    return model


@router.get("/proposal/{proposal_id}/directories")
async def get_proposal_directories(proposal_id: int) -> List[ProposalDirectories]:
    directories = await proposal_service.directories(proposal_id)
    return directories
