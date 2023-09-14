import fastapi

router = fastapi.APIRouter()


@router.get('/facility/{facility}/cycles/current', response_model=str)
async def get_current_facilty_cycle(facility: str):
    return "2023-3"
