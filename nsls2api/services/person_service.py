# Helper and utility functions for people/users
from typing import Optional

from nsls2api.api.models.person_model import Person
from nsls2api.services import bnlpeople_service
from nsls2api.services import n2sn_service

async def diagnostic_details_by_username(username: str) -> Optional[Person]:
    # TODO: Update this with some real person that we look up!

    bnl_person = await bnlpeople_service.get_person_by_username(username)
    ad_person = await n2sn_service.get_user_by_username(username)
    ad_groups = await n2sn_service.get_groups_by_username(username)

    print(bnl_person)
    print("-------")

    print(ad_person)
    print("-------")

    print(ad_groups)
    print("-------")

    # For now I am going to assume that all usernames are unique.
    if len(bnl_person) > 1:
        return

    person = Person(
        firstname=bnl_person[0]["FirstName"],
        lastname=bnl_person[0]["LastName"],
        email=ad_person[0]["mail"],
        bnl_id=bnl_person[0]["EmployeeNumber"],
    )

    return person
