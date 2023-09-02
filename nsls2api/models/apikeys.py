import datetime
from typing import Optional

import beanie
import pydantic


class ApiKey(beanie.Document):
    name: str
    value: str
    scopes: list[str]
    created_on: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    class Settings:
        name = 'api_keys'
        indexes = []
