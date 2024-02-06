import fastapi

from nsls2api._version import version as api_version
from nsls2api.api.models.stats_model import AboutModel, StatsModel
from nsls2api.services import (
    beamline_service,
    facility_service,
    proposal_service,
)

router = fastapi.APIRouter()

@router.get("/stats", response_model=StatsModel)
async def stats():
    proposals = await proposal_service.proposal_count()
    beamlines = await beamline_service.beamline_count()
    facilities = await facility_service.facilities_count()
    commissioning = len(await proposal_service.commissioning_proposals())

    faciltiy_data_health = await facility_service.is_healthy("nsls2")

    model = StatsModel(
        facility_count=facilities,
        beamline_count=beamlines,
        proposal_count=proposals,
        commissioning_proposal_count=commissioning,
        facility_data_health=faciltiy_data_health,
    )
    return model


@router.get("/about", response_model=AboutModel)
async def about():
    model = AboutModel(version=api_version, description="NSLS-II Facility API")
    return model
