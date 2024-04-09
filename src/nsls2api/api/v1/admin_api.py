from typing import Annotated

import fastapi
from fastapi import Depends, HTTPException, Request

from nsls2api.infrastructure import config
from nsls2api.infrastructure.security import (
    validate_admin_role,
    generate_api_key,
)
from nsls2api.models.apikeys import ApiUser
from nsls2api.services import background_service

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


@router.get("/admin/sync/check-status/{job_id}")
async def check_job_status(request: Request, job_id: str):
    """
    Check the status of a background job.

    :param job_id: The ID of the job to check.
    :return: The status of the job.
    """

    job = await background_service.job_by_id(job_id)
    if job is None:
        return fastapi.responses.JSONResponse(
            {"error": f"Job {job_id} not found"},
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
        )
    else:
        return job.processing_status
