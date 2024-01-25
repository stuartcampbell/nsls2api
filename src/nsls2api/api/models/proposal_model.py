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


class ProposalDirectories(pydantic.BaseModel):
    path: str
    owner: str
    group: str
    group_writable: bool
    users: list[dict[str, str]]
    groups: list[dict[str, str]]

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "path": "/nsls2/xf11id1/2021-2/20210901",
                "owner": "xf11id1",
                "group": "xf11id1",
                "group_writable": True,
                "users": [
                    {"name": "xf11id1", "permissions": "rwx"},
                    {"name": "xf11id2", "permissions": "rwx"},
                ],
                "groups": [
                    {"name": "xf11id1", "permissions": "rwx"},
                    {"name": "xf11id2", "permissions": "rwx"},
                ],
            }]
        }
    }
