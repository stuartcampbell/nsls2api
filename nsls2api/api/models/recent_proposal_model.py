import datetime
from typing import Optional

import pydantic


class RecentProposal(pydantic.BaseModel):
    proposal_id: str
    title: str
    updated: datetime.datetime
    instruments: Optional[list[str]]


class RecentProposalsModel(pydantic.BaseModel):
    count: int
    proposals: list[RecentProposal]
