import calendar
import datetime
import enum
import secrets
from typing import Optional

from beanie import WriteRules
from fastapi import Security, status, HTTPException, Request, Depends
from fastapi.security import APIKeyHeader, APIKeyQuery
from passlib.handlers.argon2 import argon2 as crypto
from pydantic_settings import BaseSettings

from nsls2api.infrastructure.config import get_settings
from nsls2api.models.apikeys import ApiKey, ApiUser, ApiUserType

TOKEN_BYTE_LENGTH = 32
API_KEY_PREFIX = "nsls2-api-"

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


def hash_api_key(api_key):
    return crypto.hash(api_key)


def verify_hashed_key(api_key, hashed_api_key):
    return crypto.verify(api_key, hashed_api_key)


async def get_api_key(
    query_key: str = Security(api_key_query),
    header_key: str = Security(api_key_header),
):
    for api_key in [query_key, header_key]:
        if api_key is not None:
            return api_key
    return None


async def generate_api_key(username: str):
    try:
        # Is there an API user for this key to be associated with
        user = await ApiUser.find_one(ApiUser.username == username)
        # If not create one
        if not user:
            print("No user found - creating user principal")
            user = ApiUser(username=username, type=ApiUserType.user)
            await user.save(link_rule=WriteRules.WRITE)

        # Actually generate the api key and add a readable prefix
        generated_key = secrets.token_hex(TOKEN_BYTE_LENGTH + 4)
        secret_key = f"{API_KEY_PREFIX}{generated_key}"

        # Hash the key to store in the database
        to_hash = hash_api_key(secret_key)

        prefix_length = len(API_KEY_PREFIX)

        new_key = ApiKey(
            user=user,
            username=username,
            first_eight=secret_key[prefix_length : prefix_length + 8],
            secret_key=secret_key,  # TODO: After development - we will not be storing this one in the database
            hashed_key=to_hash,
            expires_after=None,
        )

        # user.user_api_keys.append(new_key)
        await user.update(link_rule=WriteRules.WRITE)
        await new_key.save(link_rule=WriteRules.WRITE)

        # Now that we have saved a new key for this user, we should invalidate any other keys

        return {"key:": secret_key}

    except Exception as e:
        print(e)
        raise e


async def lookup_api_key(token: str) -> ApiKey:
    """
    :param token: The token used for API key lookup
    :return: The ApiKey object matching the supplied token
    """
    prefix_length = len(API_KEY_PREFIX)

    apikey: ApiKey = await ApiKey.find_one(
        ApiKey.first_eight == token[prefix_length : prefix_length + 8], fetch_links=True
    )

    if apikey is None:
        raise LookupError(
            f"Could not find an API key matching the one supplied: {token}"
        )

    return apikey


async def verify_api_key(token: str) -> Optional[ApiKey]:
    """
    Verifies the validity of an API key.

    :param token: The API key token to verify.
    :return: Optional[ApiKey] - The validated API key if it is valid, None otherwise.
    """
    key: ApiKey = await lookup_api_key(token)
    key_valid = verify_hashed_key(token, key.hashed_key)
    if key_valid and key.valid:
        return key
    else:
        return None


class SpecialUsers(str, enum.Enum):
    anonymous = "anonymous"
    admin = "admin"


async def get_current_user(
    request: Request,
    api_key: str = Depends(get_api_key),
    settings: BaseSettings = Depends(get_settings),
):
    if api_key is not None:
        key: ApiKey = await verify_api_key(api_key)

        if key:
            return key.username
            # return {'username': key.username}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
            )
    else:
        # No form of authentication is being used.
        return SpecialUsers.anonymous


async def validate_admin_role(
    request: Request,
    api_key: str = Depends(get_api_key),
    settings: BaseSettings = Depends(get_settings),
):
    if api_key is not None:
        valid_key = await verify_api_key(api_key)
        key = await lookup_api_key(api_key)
        if key.user.role == "admin":
            return key.user.username
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin API key"
            )


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
    month = new_month % 12
    if month == 0:
        month = 12

    # Calculate the day
    day = date_now.day
    last_day_of_month = calendar.monthrange(year, month)[1]
    if day > last_day_of_month:
        day = last_day_of_month

    new_date = datetime.date(year, month, day)
    return new_date
