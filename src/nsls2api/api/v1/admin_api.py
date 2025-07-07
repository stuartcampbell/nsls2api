from typing import Annotated, Optional

import fastapi
from fastapi import Depends, HTTPException

from nsls2api.models.facilities import FacilityName
from nsls2api.api.models.proposal_model import SingleProposal
from nsls2api.infrastructure import config
from nsls2api.infrastructure.security import (
    generate_api_key,
    validate_admin_role,
)
from nsls2api.models.apikeys import (
    ApiUser,
    ApiUserResponseModel,
    ApiUserRole,
    ApiUserType,
)
from nsls2api.services import proposal_service

# router = fastapi.APIRouter()
router = fastapi.APIRouter(
    dependencies=[Depends(validate_admin_role)], include_in_schema=True, tags=["admin"]
)


@router.get("/admin/settings")
async def info(settings: Annotated[config.Settings, Depends(config.get_settings)]):
    return settings


@router.get("/admin/validate", response_model=str)
async def check_admin_validation(
    admin_user: Annotated[ApiUser, Depends(validate_admin_role)] = None,
):
    """
    :return: str - The username of the validated admin user.
    """

    if admin_user is None:
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key",
        )

    return admin_user.username


@router.post("/admin/generate-api-key/{username}")
async def generate_user_apikey(username: str, usertype: ApiUserType = ApiUserType.user):
    """
    Generate an API key for a given username.

    :param username: The username for which to generate the API key.
    :param usertype: The type of API key to generate.
    :return: The generated API key.
    """
    return await generate_api_key(username, usertype=usertype)


@router.post("/admin/proposal/generate-test")
async def generate_fake_proposal(
    add_specific_user: str | None = None,
) -> Optional[SingleProposal]:
    proposal = await proposal_service.generate_fake_test_proposal(
        FacilityName.nsls2, add_specific_user
    )

    if proposal is None:
        raise HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate a fake test proposal",
        )

    return SingleProposal(proposal=proposal)


@router.put("/admin/user/{username}/role/{role}")
async def update_user_role(username: str, role: ApiUserRole) -> ApiUserResponseModel:
    """
    Update the role of a user.

    :param username: The username of the user to update.
    :param role: The new role for the user.
    :return: The updated user object.
    """
    user = await ApiUser.find_one(ApiUser.username == username)
    if user is None:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"User {username} not found",
        )

    user.role = role
    await user.save()  # noqa

    response = ApiUserResponseModel(
        id=user.id,
        username=user.username,
        type=user.type,
        role=user.role,
        created_on=user.created_on,
        last_updated=user.last_updated,
    )

    return response
