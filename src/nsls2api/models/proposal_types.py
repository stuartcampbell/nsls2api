import datetime
from typing import Optional

import beanie
import pydantic


class ProposalType(beanie.Document):
    code: str
    facility_id: str
    description: Optional[str]
    pass_id: Optional[str]
    pass_description: Optional[str]
    created_on: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )
    last_updated: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )

    class Settings:
        name = "proposal_types"
        indexes = []
