import fastapi

from nsls2api.models.beamlines import Beamline
from nsls2api.services import beamline_service

router = fastapi.APIRouter()


@router.get('/beamline/{name}', response_model=Beamline)
async def details(name: str):
    beamline = await beamline_service.beamline_by_name(name)
    if beamline is None:
        return fastapi.responses.JSONResponse({'error': f'Beamline named {beamline} could not be found'},
                                              status_code=404)
    return beamline
