import fastapi

from nsls2api.api.models.stats_model import StatsModel
from nsls2api.services import proposal_service, facility_service, beamline_service

router = fastapi.APIRouter()


@router.get('/stats', response_model=StatsModel)
async def stats():
    proposals = await proposal_service.proposal_count()
    beamlines = await beamline_service.beamline_count()
    facilities = await facility_service.facilities_count()
    commissioning = len(await proposal_service.commissioning_proposals())

    model = StatsModel(facility_count=facilities, beamline_count=beamlines, proposal_count=proposals,
                       commissioning_proposal_count=commissioning)
    return model
