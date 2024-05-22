import datetime
from typing import Optional

import beanie
import pydantic


class ProposalType(beanie.Document):
    code: str
    facility_id: str | None = None
    description: Optional[str] = None
    pass_id: Optional[str] = None
    pass_description: Optional[str] = None
    ups_id: Optional[str] = None
    ups_description: Optional[str] = None
    ups_type: Optional[str] = None
    created_on: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )
    last_updated: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )

    class Settings:
        name = "proposal_types"
        indexes = []
