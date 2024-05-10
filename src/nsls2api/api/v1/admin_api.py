from typing import Annotated

import fastapi
from fastapi import Depends, HTTPException

from nsls2api.infrastructure import config
from nsls2api.infrastructure.logging import logger
from nsls2api.infrastructure.security import (
    validate_admin_role,
    generate_api_key,
)
from nsls2api.models.apikeys import ApiUser
from nsls2api.services import proposal_service, slack_service

# router = fastapi.APIRouter()
router = fastapi.APIRouter(
    dependencies=[Depends(validate_admin_role)], include_in_schema=True, tags=["admin"]
)


@router.get("/admin/settings")  # , include_in_schema=False)
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


@router.post("/admin/generate_api_key/{username}")
async def generate_user_apikey(username: str):
    """
    Generate an API key for a given username.

    :param username: The username for which to generate the API key.
    :return: The generated API key.
    """
    return await generate_api_key(username)


@router.post("/admin/slack/create-proposal-channel/{proposal_id}")
async def create_slack_channel(proposal_id: str):
    proposal = await proposal_service.proposal_by_id(int(proposal_id))

    if proposal is None:
        return fastapi.responses.JSONResponse(
            {"error": f"Proposal {proposal_id} not found"}, status_code=404
        )

    channel_name = proposal_service.slack_channel_name_for_proposal(proposal_id)

    if channel_name is None:
        return fastapi.responses.JSONResponse(
            {"error": f"Slack channel name cannot be found for proposal {proposal_id}"},
            status_code=404, )

    channel_id = await slack_service.create_channel(channel_name, True,
                                          description=f"Discussion related to proposal {proposal_id}")

    if channel_id is None:
        return fastapi.responses.JSONResponse({"error": f"Slack channel creation failed for proposal {proposal_id}"}, status_code=500)

    logger.info(f"Created slack channel '{channel_name}' for proposal {proposal_id}.")

    # Store the created slack channel ID
    proposal.slack_channel_id = channel_id
    await proposal.save()
