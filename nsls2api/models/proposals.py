import datetime
from typing import Optional

import beanie
import pydantic
import pymongo


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
        indexes = [
            pymongo.IndexModel(keys=[("proposal_id", pymongo.DESCENDING)], name="proposal_id_descend"),
            pymongo.IndexModel(keys=[("last_updated", pymongo.DESCENDING)], name="last_updated_descend"),
            pymongo.IndexModel(keys=[("users.username", pymongo.ASCENDING)], name="users_username_ascend"),
            pymongo.IndexModel(keys=[("users.email", pymongo.ASCENDING)], name="users_email_ascend"),
            pymongo.IndexModel(keys=[("users.bnl_id", pymongo.ASCENDING)], name="users_bnl_id_ascend"),
            pymongo.IndexModel(keys=[("users.last_name", pymongo.ASCENDING)], name="users_last_name_ascend"),
            pymongo.IndexModel(keys=[("safs.saf_id", pymongo.DESCENDING)], name="safs_saf_id_descend"),
        ]


class UsernamesOnly(pydantic.BaseModel):
    username: str

    class Settings:
        projection = {
            "username": "$username",
        }
