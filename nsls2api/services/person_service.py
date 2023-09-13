# Helper and utility functions for people/users
from typing import Optional

from nsls2api.api.models.person_model import Person, ActiveDirectoryUser, PersonSummary
from nsls2api.services import bnlpeople_service
from nsls2api.services import n2sn_service
from nsls2api.services.pass_service import get_proposals_by_person


async def summary_details_by_username(username: str) -> Optional[PersonSummary]:
    diag_person = await diagnostic_details_by_username(username)
    # Now lets return a Person that only contains a limited
    person = PersonSummary(
        firstname=diag_person.firstname,
        lastname=diag_person.lastname,
        email=diag_person.email,
        username=username,
        institution=diag_person.institution,
    )
    return person


async def diagnostic_details_by_username(username: str) -> Optional[Person]:
    try:
        bnl_person = await bnlpeople_service.get_person_by_username(username)
        ad_person: ActiveDirectoryUser = await n2sn_service.get_user_by_username(
            username
        )
        ad_groups = await n2sn_service.get_groups_by_username(username)
        proposals = await get_proposals_by_person(bnl_person.EmployeeNumber)
    except LookupError as error:
        raise LookupError(
            f"Error obtaining diagnostic details for username of {username}"
        ) from error

    print(bnl_person)
    print("-------")

    print(ad_person)
    print("-------")

    print(ad_groups)
    print("-------")

    print(proposals)
    print("-------")

    person = Person(
        firstname=bnl_person.FirstName,
        lastname=bnl_person.LastName,
        email=ad_person.mail,
        username=username,
        institution=bnl_person.Institution,
        bnl_id=bnl_person.EmployeeNumber,
        account_locked=ad_person.locked,
    )
    return person
