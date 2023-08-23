import fastapi

from fastapi import HTTPException

router = fastapi.APIRouter()

@router.get('/person/username/{username}')
async def get_person_by_username(username: str):
    pass

