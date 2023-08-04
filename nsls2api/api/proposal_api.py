import fastapi

from api.models.recent_proposal_model import RecentProposalsModel, RecentProposal
from api.models.proposal_model import UsernamesModel
from models.proposals import Proposal
from services import proposal_service

router = fastapi.APIRouter()


@router.get('/proposals/recent/{count}', response_model=RecentProposalsModel)
async def recent(count: int):
    count = max(1, count)
    proposals = await proposal_service.recently_updated(count)

    proposal_models = [
        RecentProposal(proposal_id=p.proposal_id, title=p.title, updated=p.last_updated)
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


@router.get('/proposal/{proposal_id}/usernames', response_model=UsernamesModel)
async def usernames(proposal_id: str):
    proposal = await proposal_service.proposal_by_id(proposal_id)
    if proposal is None:
        return fastapi.responses.JSONResponse({'error': f'Proposal {proposal_id} not found'}, status_code=404)

    usernames = [
        u.username
        for u in proposal.users if u.username is not None
    ]
    model = UsernamesModel(usernames=usernames)
    return model
