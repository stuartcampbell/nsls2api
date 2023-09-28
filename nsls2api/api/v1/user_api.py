from typing import Annotated

import fastapi
from fastapi import Depends
from infrastructure.security import (
    get_current_user,
)

from nsls2api.api.models.person_model import Person, DataSessionAccess
from nsls2api.services import (
    bnlpeople_service,
    person_service,
)

router = fastapi.APIRouter()


@router.get("/person/username/{username}", response_model=Person)
async def get_person_from_username(username: str):
    bnl_person = await bnlpeople_service.get_person_by_username(username)
    print(bnl_person)
    if len(bnl_person) == 1:
        person = Person(
            firstname=bnl_person[0]["FirstName"],
            lastname=bnl_person[0]["LastName"],
            email=bnl_person[0]["BNLEmail"],
            bnl_id=bnl_person[0]["EmployeeNumber"],
        )
        return person
    else:
        return fastapi.responses.JSONResponse(
            {"error": f"Multiple people with username {username} found."},
            status_code=404,
        )


@router.get("/person/email/{email}")
async def get_person_from_email(username: str):
    pass


@router.get("/person/me", response_model=str)
async def get_myself(current_user: Annotated[Person, Depends(get_current_user)]):
    return current_user


@router.get("/data-session/{username}", response_model=DataSessionAccess, tags=["data"])
@router.get(
    "/data_session/{username}",
    response_model=DataSessionAccess,
    tags=["data"],
    include_in_schema=False,
    description="Deprecated endpoint included for Tiled compatibility.",
)
async def get_data_sessions_by_username(username: str):
    data_access = await person_service.data_sessions_by_username(username)
    return data_access
