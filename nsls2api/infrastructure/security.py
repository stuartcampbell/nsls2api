import enum
import secrets

from fastapi import (
    Security, status, HTTPException,
    Request, Depends)
from fastapi.security import APIKeyHeader, APIKeyQuery, APIKeyCookie
from passlib.handlers.argon2 import argon2 as crypto
from pydantic_settings import BaseSettings

from nsls2api.infrastructure.config import get_settings
from nsls2api.models.apikeys import ApiKey, Principal

# NOTE: This is not a real key - don't bother trying it.
API_KEYS = [
    "nsls2-06b7286be270c19b1db2c3fa2a374488f908e11b2b0d6b1ef41ff55b57398322"
]

TOKEN_BYTE_LENGTH = 32
API_KEY_COOKIE_NAME = "nsls2_api_key"

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_COOKIE_NAME, auto_error=False)


async def get_api_key(
        api_key_query: str = Security(api_key_query),
        api_key_header: str = Security(api_key_header),
        api_key_cookie: str = Security(api_key_cookie),
):
    for api_key in [api_key_query, api_key_header, api_key_cookie]:
        if api_key is not None:
            return api_key
    return None


async def generate_api_key(principal: Principal, api_scopes: list[str], note: str = None) -> ApiKey:
    if api_scopes is None:
        scopes = ["inherit"]
    else:
        # TODO: Need some logic here to make sure we are allowed to grant
        #  these scopes to this principal
        scopes = api_scopes

    # The standard 32 byes of entropy,
    # plus 4 more for extra safety since we store the first eight HEX chars.
    token = f"nsls2-{secrets.token_hex(TOKEN_BYTE_LENGTH + 4)}"
    hash_token = crypto.encrypt(token)

    user_key = ApiKey(
        principal=principal,
        hashed_secret=hash_token,
        first_eight=token[:8],
        note=note,
        scopes=scopes
    )

    await user_key.save()

    return user_key


class SpecialUsers(str, enum.Enum):
    public = "public"
    admin = "admin"


async def get_current_principal(request: Request, api_key: str = Depends(get_api_key),
                                settings: BaseSettings = Depends(get_settings)):
    if api_key is not None:
        try:
            secret = bytes.fromhex(api_key)
        except Exception:
            # Not valid hex, therefore not a valid API key
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

        # Do auth stuff
    else:
        # No form of authentication is being used.
        principal = SpecialUsers.public

    return principal
