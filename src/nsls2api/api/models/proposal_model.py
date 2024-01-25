import datetime
from typing import Optional

import pydantic


class UsernamesModel(pydantic.BaseModel):
    usernames: list[str]

    model_config = {
        "json_schema_extra": {"examples": [{"usernames": ["rdeckard", "rbatty"]}]}
    }


class CommissioningProposalsModel(pydantic.BaseModel):
    count: int
    commissioning_proposals: list[str]


class RecentProposal(pydantic.BaseModel):
    proposal_id: str
    title: str
    updated: datetime.datetime
    instruments: Optional[list[str]]


class RecentProposalsModel(pydantic.BaseModel):
    count: int
    proposals: list[RecentProposal]


class ProposalSummary(pydantic.BaseModel):
    proposal_id: str
    title: str

class ProposalDiagnostics(pydantic.BaseModel):
    proposal_id: str
    title: str
    updated: datetime.datetime