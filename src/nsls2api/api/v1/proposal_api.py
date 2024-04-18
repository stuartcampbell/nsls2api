from typing import Annotated
import fastapi
from fastapi import Depends, HTTPException, Query, Request

from nsls2api.api.models.proposal_model import (
    CommissioningProposalsList,
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
from nsls2api.models.jobs import JobActions, JobSyncParameters
from nsls2api.models.proposals import Proposal
from nsls2api.services import background_service, proposal_service
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
    try:
        proposals = await proposal_service.commissioning_proposals(beamline=beamline)
        if proposals is None:
            return fastapi.responses.JSONResponse(
                {"error": "Commissioning Proposals not found"}, status_code=404
            )
    except LookupError as e:
        return fastapi.responses.JSONResponse(
            {"error": e.args[0]},
            status_code=404,
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

    response_model = {
        "proposals": proposal_list,
        "page_size": page_size,
        "page": page,
        "count": len(proposal_list),
    }

    return response_model


@router.get("/proposal/{proposal_id}", response_model=SingleProposal)
async def get_proposal(proposal_id: int):
    try:
        proposal = await proposal_service.proposal_by_id(proposal_id)
        if proposal is None:
            return fastapi.responses.JSONResponse(
                {"error": f"Proposal {proposal_id} not found"}, status_code=404
            )
    except LookupError as e:
        return fastapi.responses.JSONResponse(
            {"error": e.args[0]},
            status_code=404,
        )
    response_model = SingleProposal(proposal=proposal)
    return response_model


@router.get(
    "/proposal/sync/{proposal_id}",
    dependencies=[Depends(get_current_user)],
    include_in_schema=True,
)
async def sync_proposal(request: Request, proposal_id: int) -> Proposal:
    sync_params = JobSyncParameters(proposal_id=str(proposal_id))
    job = await background_service.create_background_job(
        JobActions.synchronize_proposal, sync_parameters=sync_params,
    )
    return job


@router.get("/proposal/types/sync/{facility}", include_in_schema=True)
async def sync_proposal_types(facility: FacilityName = FacilityName.nsls2):
    sync_params = JobSyncParameters(facility=facility)
    job = await background_service.create_background_job(
        JobActions.synchronize_proposal_types, sync_parameters=sync_params,
    )
    return job


@router.get("/proposal/{proposal_id}/users", response_model=ProposalUserList)
async def get_proposals_users(proposal_id: int):
    try:
        users = await proposal_service.fetch_users_on_proposal(proposal_id)
        if users is None:
            return fastapi.responses.JSONResponse(
                {"error": f"Users not found for proposal {proposal_id}"},
                status_code=404,
            )
    except LookupError as e:
        return fastapi.responses.JSONResponse(
            {"error": e.args[0]},
            status_code=404,
        )

    response_model = ProposalUserList(
        proposal_id=str(proposal_id), users=users, count=len(users)
    )
    return response_model


@router.get(
    "/proposal/{proposal_id}/principal-investigator", response_model=ProposalUser
)
async def get_proposal_principal_investigator(proposal_id: int):
    try:
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
    except LookupError as e:
        return fastapi.responses.JSONResponse(
            {"error": e.args[0]},
            status_code=404,
        )

    response_model = ProposalUser(
        proposal_id=str(proposal_id), user=principal_investigator[0]
    )
    return response_model


@router.get("/proposal/{proposal_id}/usernames", response_model=UsernamesList)
async def get_proposal_usernames(proposal_id: int):
    try:
        # Check to see if proposal exists
        if not await proposal_service.exists(proposal_id):
            return fastapi.responses.JSONResponse(
                {"error": f"Proposal {proposal_id} not found"}, status_code=404
            )
    except LookupError as e:
        return fastapi.responses.JSONResponse(
            {"error": e.args[0]},
            status_code=404,
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
