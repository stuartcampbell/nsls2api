# Helper and utility functions for people/users
from typing import Optional

from nsls2api.api.models.person_model import Person


def diagnostic_details_by_username(username: str) -> Optional[Person]:
    # TODO: Update this with some real person that we look up!

    person = Person(firstname="James", lastname="Moriarty", email="prof@crime.com", bnl_id="X6666X")

    return person
