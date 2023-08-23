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
