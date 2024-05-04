import datetime
from typing import Optional

import beanie
import pydantic


class Facility(beanie.Document):
    name: str
    facility_id: str
    fullname: str
    pass_facility_id: Optional[str] = None
    data_admins: Optional[list[str]] = []
    created_on: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )
    last_updated: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )

    class Settings:
        name = "facilities"
        indexes = []
