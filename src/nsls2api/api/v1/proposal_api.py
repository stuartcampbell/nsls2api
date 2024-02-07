from typing import Annotated
import fastapi
from fastapi import Depends, HTTPException, Query

from nsls2api.api.models.proposal_model import (
    CommissioningProposalsList,
    PageLinks,
    ProposalDirectoriesList,
    ProposalFullDetailsList,
    ProposalUser,
    ProposalUserList,
    RecentProposal,
    RecentProposalsList,
    SingleProposal,
)
from nsls2api.api.models.proposal_model import UsernamesList
from nsls2api.infrastructure.security import get_current_user
from nsls2api.models.proposals import Proposal
from nsls2api.services import proposal_service
from nsls2api.api.models.facility_model import FacilityName


router = fastapi.APIRouter()


@router.get("/proposals/recent/{count}", response_model=RecentProposalsList)
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
    model = RecentProposalsList(count=count, proposals=proposal_models)

    return model


@router.get("/proposals/commissioning", response_model=CommissioningProposalsList)
async def get_commissioning_proposals(beamline: str | None = None):
    proposals = await proposal_service.commissioning_proposals(beamline=beamline)
    if proposals is None:
        return fastapi.responses.JSONResponse(
            {"error": "Commissioning Proposals not found"}, status_code=404
        )
    model = CommissioningProposalsList(
        count=len(proposals), commissioning_proposals=proposals
    )
    return model


@router.get("/proposals/", response_model=ProposalFullDetailsList)
async def get_proposals(
    proposal_id: Annotated[list[str], Query()] = [],
    beamline: Annotated[list[str], Query()] = [],
    cycle: Annotated[list[str], Query()] = [],
    facility: Annotated[list[FacilityName], Query()] = [FacilityName.nsls2],
    page_size: int = 10,
    page: int = 1,
    include_directories: bool = False,
    request: fastapi.Request = None,
):
    proposal_list = await proposal_service.fetch_proposals(
        proposal_id=proposal_id,
        beamline=beamline,
        cycle=cycle,
        facility=facility,
        page_size=page_size,
        page=page,
        include_directories=include_directories,
    )

    if page > 1:
        previous_page = page - 1


    links = PageLinks(
        first=f"{request.base_url}/proposals/?page_size={page_size}&page=1",
        next=f"/proposals/?page_size={page_size}&page={page+1}",
        previous=f"/proposals/?page_size={page_size}&page={previous_page}",
    )

    response_model = {
        "proposals": proposal_list,
        "page_size": page_size,
        "page": page,
        "count": len(proposal_list),
        "links": links,
    }

    return response_model


@router.get("/proposal/{proposal_id}", response_model=SingleProposal)
async def get_proposal(proposal_id: int, beamline: str | None = None):
    proposal = await proposal_service.proposal_by_id(proposal_id)
    if proposal is None:
        return fastapi.responses.JSONResponse(
            {"error": f"Proposal {proposal_id} not found"}, status_code=404
        )
    response_model = SingleProposal(proposal=proposal)
    return response_model


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


@router.get("/proposal/{proposal_id}/users", response_model=ProposalUserList)
async def get_proposals_users(proposal_id: int):
    users = await proposal_service.fetch_users_on_proposal(proposal_id)
    if users is None:
        return fastapi.responses.JSONResponse(
            {"error": f"Users not found for proposal {proposal_id}"}, status_code=404
        )
    response_model = ProposalUserList(
        proposal_id=str(proposal_id), users=users, count=len(users)
    )
    return response_model


@router.get(
    "/proposal/{proposal_id}/principal-investigator", response_model=ProposalUser
)
async def get_proposal_principal_investigator(proposal_id: int):
    principal_investigator = await proposal_service.pi_from_proposal(proposal_id)

    if len(principal_investigator) == 0:
        return fastapi.responses.JSONResponse(
            {"error": f"PI not found for proposal {proposal_id}"},
            status_code=404,
        )
    elif len(principal_investigator) > 1:
        return fastapi.responses.JSONResponse(
            {"error": f"Proposal {proposal_id} contains more than one PI"},
            status_code=422,
        )

    response_model = ProposalUser(
        proposal_id=str(proposal_id), user=principal_investigator[0]
    )
    return response_model


@router.get("/proposal/{proposal_id}/usernames", response_model=UsernamesList)
async def get_proposal_usernames(proposal_id: int):
    # Check to see if proposal exists
    if not await proposal_service.exists(proposal_id):
        return fastapi.responses.JSONResponse(
            {"error": f"Proposal {proposal_id} not found"}, status_code=404
        )

    proposal_usernames = await proposal_service.fetch_usernames_from_proposal(
        proposal_id
    )
    response_model = UsernamesList(
        usernames=proposal_usernames,
        proposal_id=str(proposal_id),
        count=len(proposal_usernames),
    )
    return response_model


@router.get("/proposal/{proposal_id}/directories")
async def get_proposal_directories(proposal_id: int) -> ProposalDirectoriesList:
    try:
        directories = await proposal_service.directories(proposal_id)
        if directories is None:
            return fastapi.responses.JSONResponse(
                {"error": f"Directories not found for proposal {proposal_id}"},
                status_code=404,
            )
    except LookupError as e:
        return fastapi.responses.JSONResponse(
            {"error": e.args[0]},
            status_code=404,
        )

    response_model = ProposalDirectoriesList(
        directories=directories,
        directory_count=len(directories),
    )
    return response_model
