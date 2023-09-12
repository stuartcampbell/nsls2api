import secrets
from typing import Optional

from fastapi import Security, status, HTTPException
from fastapi.security import APIKeyHeader
from passlib.handlers.argon2 import argon2 as crypto

from nsls2api.models.apikeys import ApiKey

# NOTE: This is not a real key - don't bother trying it.
API_KEYS = [
    "nsls2-06b7286be270c19b1db2c3fa2a374488f908e11b2b0d6b1ef41ff55b57398322"
]

TOKEN_BYTE_LENGTH = 32

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def get_api_key(
        api_key_header: str = Security(api_key_header),
) -> str:
    if api_key_header in API_KEYS:
        return api_key_header

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate API KEY",
    )

async def generate_token(username: str, name: Optional[str], scopes: list[str]) -> str:
    token = f"nsls2-{secrets.token_hex(TOKEN_BYTE_LENGTH)}"
    hash_token = crypto.encrypt(token)

    user_key = ApiKey(username=username, value=hash_token, )

    await user_key.save()

    return token

