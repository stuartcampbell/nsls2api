import datetime
import pydantic

class RecentProposal(pydantic.BaseModel):
    proposal_id: str
    title: str
    updated: datetime.datetime

class RecentProposalsModel(pydantic.BaseModel):
    count: int
    proposals: list[RecentProposal]