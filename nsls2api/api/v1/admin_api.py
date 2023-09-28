from typing import Annotated

import fastapi
from fastapi import Depends

from nsls2api.infrastructure.security import validate_admin_role, generate_api_key
from nsls2api.models.apikeys import ApiUser

router = fastapi.APIRouter()
# router = fastapi.APIRouter(dependencies=[Depends(validate_admin_role)])


@router.get('/admim/validate', response_model=str)
async def check_admin_validation(admin_user: Annotated[ApiUser, Depends(validate_admin_role)]):
    """
    :param admin_user: Annotated[ApiUser, Depends(validate_admin_role)] - The admin user to be checked for validation.
    :return: str - The username of the validated admin user.
    """
    return admin_user.username


@router.post('/admin/generate_api_key/{username}')
async def generate_user_apikey(username: str):
    """
    Generate an API key for a given username.

    :param username: The username for which to generate the API key.
    :return: The generated API key.
    """
    return await generate_api_key(username)



# The following endpoints are 'pass-through' routes to underlying services
# They are here for convenience only