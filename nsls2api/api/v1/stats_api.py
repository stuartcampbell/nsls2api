import fastapi

from api.models.stats_model import StatsModel
from services import proposal_service, facility_service, beamline_service

router = fastapi.APIRouter()

@router.get('/stats', response_model=StatsModel)
async def stats():
    proposals = await proposal_service.proposal_count()
    beamlines = await beamline_service.beamline_count()
    facilities = await facility_service.facilities_count()

    model = StatsModel(facility_count=facilities, beamline_count=beamlines, proposal_count=proposals)
    return model
