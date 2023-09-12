import datetime
from typing import Optional

import beanie
import pydantic


class ApiKey(beanie.Document):
    username: str
    value: str
    name: Optional[str]
    scopes: list[str]
    created_on: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    class Settings:
        name = 'api_keys'
        indexes = []
