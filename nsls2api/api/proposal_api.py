import fastapi

from api.models.proposal_model import UsernamesModel
from api.models.recent_proposal_model import RecentProposalsModel, RecentProposal
from models.proposals import Proposal, User
from services import proposal_service

router = fastapi.APIRouter()


@router.get('/proposals/recent/{count}', response_model=RecentProposalsModel)
async def recent(count: int, beamline: str | None = None):
    count = max(1, count)
    proposals = await proposal_service.recently_updated(count, beamline=beamline)

    proposal_models = [
        RecentProposal(proposal_id=p.proposal_id, title=p.title, updated=p.last_updated, instruments=p.instruments)
        for p in proposals
    ]
    model = RecentProposalsModel(count=count, proposals=proposal_models)

    return model


@router.get('/proposal/{proposal_id}', response_model=Proposal)
async def details(proposal_id: str):
    proposal = await proposal_service.proposal_by_id(proposal_id)
    if proposal is None:
        return fastapi.responses.JSONResponse({'error': f'Proposal {proposal_id} not found'}, status_code=404)
    return proposal


@router.get('/proposal/{proposal_id}/users', response_model=list[User])
async def users(proposal_id: str):
    users = await proposal_service.users_from_proposal(proposal_id)
    return users


@router.get('/proposal/{proposal_id}/pi', response_model=list[User])
async def users(proposal_id: str):
    principle_invesigator = await proposal_service.pi_from_proposal(proposal_id)

    if len(principle_invesigator) == 0:
        return fastapi.responses.JSONResponse({'error': f'PI not found for proposal {proposal_id}'}, status_code=404)
    elif len(principle_invesigator) > 1:
        return fastapi.responses.JSONResponse({'error': f'Proposal {proposal_id} contains more than one PI'},
                                              status_code=422)

    return principle_invesigator


@router.get('/proposal/{proposal_id}/usernames', response_model=UsernamesModel)
async def usernames(proposal_id: str):
    # Check to see if proposal exists
    if not await proposal_service.exists(proposal_id):
        return fastapi.responses.JSONResponse({'error': f'Proposal {proposal_id} not found'}, status_code=404)

    proposal_usernames = await proposal_service.usernames_from_proposal(proposal_id)
    model = UsernamesModel(usernames=proposal_usernames)

    return model
