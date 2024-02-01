import datetime
from typing import Optional

import pydantic

from nsls2api.models.proposals import Proposal, User


class UsernamesList(pydantic.BaseModel):
    usernames: list[str]
    proposal_id: Optional[str]
    count: int

    model_config = {
        "json_schema_extra": {"examples": [{"usernames": ["rdeckard", "rbatty"]}]}
    }


class CommissioningProposalsList(pydantic.BaseModel):
    count: int
    commissioning_proposals: list[str]


class RecentProposal(pydantic.BaseModel):
    proposal_id: str
    title: str
    updated: datetime.datetime
    instruments: Optional[list[str]]


class RecentProposalsList(pydantic.BaseModel):
    count: int
    proposals: list[RecentProposal]


class ProposalSummary(pydantic.BaseModel):
    proposal_id: str
    title: str


class SingleProposal(pydantic.BaseModel):
    proposal: Proposal


class ProposalUserList(pydantic.BaseModel):
    proposal_id: str
    users: list[User]
    count: int


class ProposalUser(pydantic.BaseModel):
    proposal_id: str
    user: User


class ProposalDirectories(pydantic.BaseModel):
    path: str
    owner: str
    group: str | None = ""
    group_writable: bool | None = False
    users: list[dict[str, str]]
    groups: list[dict[str, str]]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
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
                }
            ]
        }
    }

# Not used - may remove 
class ACL(pydantic.BaseModel):
    entity: str
    permissions: str
    
# Not used - may remove 
class Directory(pydantic.BaseModel):
    path: str
    is_aboslute: bool
    owner: str
    group: str
    acls: list[ACL] | None = []   

# Not used - may remove 
class ProposalDirectorySkeleton(pydantic.BaseModel):
    asset_directories: list[Directory]

class ProposalDirectoriesList(pydantic.BaseModel):
    directory_count: int
    directories: list[ProposalDirectories]


class ProposalFullDetails(Proposal):
    directories: list[ProposalDirectories] | None = None


class ProposalFullDetailsList(pydantic.BaseModel):
    proposals: list[ProposalFullDetails]
    count: int
    page_size: int | None = None
    page: int | None = None
