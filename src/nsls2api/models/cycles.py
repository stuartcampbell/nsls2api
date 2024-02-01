import datetime
from typing import Optional

import beanie
import pydantic


class Cycle(beanie.Document):
    name: str
    accepting_proposals: Optional[bool]
    current_operating_cycle: bool = False
    active: bool = False
    end_date: Optional[datetime.datetime]
    facility: str
    pass_description: Optional[str]
    pass_id: Optional[str]
    start_date: Optional[datetime.datetime]
    year: str
    proposals: Optional[list[str]]
    created_on: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )
    last_updated: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )

    class Settings:
        name = "cycles"
        indexes = []
