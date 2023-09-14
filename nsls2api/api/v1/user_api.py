import fastapi

from nsls2api.api.models.person_model import Person
from nsls2api.services import bnlpeople_service

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
            bnl_id=bnl_person[0]["EmployeeNumber"]
        )
        return person
    else:
        return fastapi.responses.JSONResponse(
            {"error": f"Multiple people with username {username} found."}, status_code=404
        )


@router.get("/person/email/{email}")
async def get_person_from_email(username: str):
    pass
