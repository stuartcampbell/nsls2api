import calendar
import datetime
import enum
from typing import Optional
from uuid import UUID, uuid4

import beanie
import pydantic
from pydantic import Field


def default_apikey_expiration(months: int = 6) -> datetime:
    """
    Default Apikey Expiration

    The `default_apikey_expiration` method calculates the expiration date for an API key based on the given number of months.

    :param months: The number of months after which the API key should expire. Defaults to 6 if not provided. (type: int)

    :return: The calculated expiration date as a `datetime` object. (type: datetime)

    Example usage:
        expiration_date = default_apikey_expiration(10)
        print(expiration_date)
        # Output: 2023-12-26

    Dependencies:
        This method has dependencies on the following modules:
        - datetime
        - calendar

    """
    date_now = datetime.datetime.now()
    new_month = date_now.month + months

    # Calculate the year
    year = date_now.year + int(new_month / 12)

    # Calculate the month
    month = (new_month % 12)
    if month == 0:
        month = 12

    # Calculate the day
    day = date_now.day
    last_day_of_month = calendar.monthrange(year, month)[1]
    if day > last_day_of_month:
        day = last_day_of_month

    new_date = datetime.date(year, month, day)
    return new_date


class PrincipalType(str, enum.Enum):
    user = "user"
    service = "service"


class Principal(beanie.Document):
    id: UUID = Field(default_factory=uuid4)
    username: str
    type: PrincipalType


class ApiKey(beanie.Document):
    principal: Principal
    first_eight: str
    hashed_secret: str
    note: Optional[pydantic.constr(min_length=8, max_length=8)]
    scopes: Optional[list[str]] = pydantic.Field(..., example=["inherit"])
    valid: bool = True
    expires_after: Optional[datetime.datetime] = pydantic.Field(default_factory=default_apikey_expiration)
    created_on: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    class Settings:
        name = 'api_keys'
        indexes = []
