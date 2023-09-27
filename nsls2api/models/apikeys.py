import calendar
import datetime
import enum
from typing import Optional, List
from uuid import UUID, uuid4

import beanie
import pydantic
import pymongo
from beanie import Link, BackLink
from pydantic import Field


def default_apikey_expiration(months: int = 6) -> datetime.date:
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


class ApiUserType(str, enum.Enum):
    user = "user"
    service = "service"


class ApiUserRole(str, enum.Enum):
    user = "user"
    staff = "staff"
    admin = "admin"


class ApiUser(beanie.Document):
    id: UUID = Field(default_factory=uuid4)
    username: str
    type: ApiUserType
    role: ApiUserRole = ApiUserRole.user
    created_on: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    user_api_keys: BackLink["ApiKey"] = Field(original_field="user")
    # user_api_keys: Optional[List[BackLink["ApiKey"]]]= Field(original_field="user")

    class Settings:
        name = 'api_users'
        indexes = [
            pymongo.IndexModel(keys=[("username", pymongo.ASCENDING)], name="username_ascend", unique=True),
            pymongo.IndexModel(keys=[("type", pymongo.ASCENDING)], name="type_ascend"),
            pymongo.IndexModel(keys=[("role", pymongo.ASCENDING)], name="role_ascend"),
            pymongo.IndexModel(keys=[("created_date", pymongo.DESCENDING)], name="created_date_descend"),
            pymongo.IndexModel(keys=[("last_login", pymongo.DESCENDING)], name="last_login_descend"),
        ]


class ApiKey(beanie.Document):
    user: Link[ApiUser]
    username: str
    first_eight: pydantic.constr(min_length=8, max_length=8)
    secret_key: str  # TODO: After development - we will not be storing this one in the database
    hashed_key: str
    note: Optional[str] = ""
    # scopes: Optional[list[str]] = pydantic.Field(..., example=["inherit"])
    valid: bool = True
    expires_after: Optional[datetime.datetime] = pydantic.Field(default_factory=default_apikey_expiration)
    created_on: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    class Settings:
        name = 'api_keys'
        keep_nulls = False
        indexes = [
            pymongo.IndexModel(keys=[("created_date", pymongo.DESCENDING)], name="created_date_descend"),
            pymongo.IndexModel(keys=[("last_login", pymongo.DESCENDING)], name="last_login_descend"),
            pymongo.IndexModel(keys=[("first_eight", pymongo.ASCENDING)], name="first_eight_ascend", unique=True),
            pymongo.IndexModel(keys=[("note", pymongo.TEXT)], name="apikey_text"),
        ]
