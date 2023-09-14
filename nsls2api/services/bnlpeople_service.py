from typing import Optional

from .helpers import _call_async_webservice
from ..api.models.person_model import BNLPerson

base_url = 'https://api.bnl.gov/BNLPeople'


async def get_all_people():
    url = f'{base_url}/api/BNLPeople'
    people = await _call_async_webservice(url)
    return people


async def get_person_by_username(username: str) -> Optional[BNLPerson]:
    url = f'{base_url}/api/BNLPeople?accountName={username}'
    person = await _call_async_webservice(url)
    if len(person) == 0 or len(person) > 1:
        raise LookupError(f"BNL People could not find a person with a username of {username}")
    return BNLPerson(**person[0])


async def get_person_by_id(lifenumber: str):
    url = f'{base_url}/api/BNLPeople?employeeNumber={lifenumber}'
    person = await _call_async_webservice(url)
    if len(person) == 0 or len(person) > 1:
        raise LookupError(f"BNL People could not find a person with an employee/life number of {lifenumber}")
    return person


async def get_person_by_email(email: str):
    url = f'{base_url}/api/BNLPeople?email={email}'
    person = await _call_async_webservice(url)
    return person


async def get_people_by_department(department_code: str):
    url = f'{base_url}/api/BNLPeople?departmentCode={department_code}'
    people = await _call_async_webservice(url)
    return people


async def get_people_by_status(status: str):
    if status.title() not in ("Active", "Inactive", "Pending"):
        raise ValueError("Status must be either 'Active', 'Inactive', 'Pending'")
    url = f"{base_url}/api/BNLPeople?status={status}"
    people = await _call_async_webservice(url)
    return people


async def get_people_by_calcstatus(calculated_status: str):
    if calculated_status.title() not in ("Active", "Inactive"):
        raise ValueError("Calculated Status must be either 'Active', 'Inactive'")
    url = f'{base_url}/api/BNLPeople?status={calculated_status}'
    people = await _call_async_webservice(url)
    return people
