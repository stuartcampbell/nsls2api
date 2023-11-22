from typing import Optional, List

from fastapi import HTTPException

from .helpers import _call_async_webservice
from ..api.models.person_model import BNLPerson
from ..models.validation_error import ValidationError

base_url = "https://api.bnl.gov/BNLPeople"


async def _call_bnlpeople_webservice(url: str):
    try:
        return await _call_async_webservice(url)
    except ValidationError as error:
        match error.status_code:
            case 503:
                message = f"BNLPeople API is unavailable (BNLPeople Error Message:{error.error_msg})"
            case _:
                message = error.error_msg
        raise HTTPException(status_code=error.status_code, detail=message)


async def get_all_people():
    url = f"{base_url}/api/BNLPeople"
    people = await _call_bnlpeople_webservice(url)
    return people


async def get_person_by_username(username: str) -> Optional[BNLPerson]:
    url = f"{base_url}/api/BNLPeople?accountName={username}"
    person = await _call_bnlpeople_webservice(url)
    if len(person) == 0 or len(person) > 1:
        raise LookupError(
            f"BNL People could not find a person with a username of {username}"
        )
    return BNLPerson(**person[0])


async def get_person_by_id(lifenumber: str) -> Optional[BNLPerson]:
    url = f"{base_url}/api/BNLPeople?employeeNumber={lifenumber}"
    person = await _call_bnlpeople_webservice(url)
    if len(person) == 0 or len(person) > 1:
        raise LookupError(
            f"BNL People could not find a person with an employee/life number of {lifenumber}"
        )
    return BNLPerson(**person[0])


async def get_person_by_email(email: str) -> Optional[BNLPerson]:
    url = f"{base_url}/api/BNLPeople?email={email}"
    person = await _call_bnlpeople_webservice(url)
    if len(person) == 0 or len(person) > 1:
        raise LookupError(
            f"BNL People could not find a person with an email of {email}"
        )
    return BNLPerson(**person[0])


async def get_people_by_department(
    department_code: str,
) -> Optional[List[BNLPerson]]:
    url = f"{base_url}/api/BNLPeople?departmentCode={department_code}"
    people = await _call_bnlpeople_webservice(url)
    if len(people) == 0:
        raise LookupError(
            f"BNL People could not find a person with the department code of {department_code}"
        )
    people_in_department = [BNLPerson(**p) for p in people]
    return people_in_department


async def get_people_by_status(status: str):
    if status.title() not in ("Active", "Inactive", "Pending"):
        raise ValueError("Status must be either 'Active', 'Inactive', 'Pending'")
    url = f"{base_url}/api/BNLPeople?status={status}"
    people = await _call_bnlpeople_webservice(url)
    return people


async def get_people_by_calcstatus(calculated_status: str):
    if calculated_status.title() not in ("Active", "Inactive"):
        raise ValueError("Calculated Status must be either 'Active', 'Inactive'")
    url = f"{base_url}/api/BNLPeople?status={calculated_status}"
    people = await _call_bnlpeople_webservice(url)
    return people
