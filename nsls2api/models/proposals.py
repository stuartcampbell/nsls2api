import datetime
from typing import Optional

import beanie
import pydantic


class SafetyForm(pydantic.BaseModel):
    saf_id: str
    status: str
    instruments: Optional[list[str]]


class User(pydantic.BaseModel):
    first_name: str
    last_name: str
    email: str
    bnl_id: Optional[str]
    username: Optional[str]
    is_pi: bool = False


class Proposal(beanie.Document):
    proposal_id: str
    data_session: str
    title: Optional[str]
    type: Optional[str]
    pass_type_id: Optional[str]
    instruments: Optional[list[str]]
    cycles: Optional[list[str]]
    users: list[User]
    safs: Optional[list[SafetyForm]]
    created_on: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    class Settings:
        name = 'proposals'
        indexes = []

