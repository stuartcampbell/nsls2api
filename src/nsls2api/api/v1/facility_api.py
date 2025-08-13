import fastapi
from fastapi import Depends
from datetime import datetime, timezone

from nsls2api.api.models.facility_model import (
    FacilityCurrentOperatingCycleResponseModel,
    FacilityCyclesResponseModel,
    FacilityName,
    FacilityCycleResponseModel
)
from nsls2api.api.models.proposal_model import CycleProposalList
from nsls2api.infrastructure.logging import logger
from nsls2api.infrastructure.security import validate_admin_role
from nsls2api.services import facility_service, proposal_service
from nsls2api.services.facility_service import (
    CycleNotFoundError,
    CycleOperationError,
    CycleUpdateError,
    CycleVerificationError,
)

router = fastapi.APIRouter()


@router.get(
    "/facility/{facility}/cycles/current",
    response_model=FacilityCurrentOperatingCycleResponseModel,
    include_in_schema=True,
)
async def get_current_operating_cycle(facility: FacilityName):
    current_cycle = await facility_service.current_operating_cycle(facility.name)
    if current_cycle is None:
        return fastapi.responses.JSONResponse(
            {
                "error": f"No current operating cycle was found for facility {facility.name}"
            },
            status_code=404,
        )

    # TODO: Maybe add a health check here
    # print("Are we healthy ? ")
    # print(await facility_service.is_healthy(facility.name))

    response_model = FacilityCurrentOperatingCycleResponseModel(
        facility=facility.name, cycle=current_cycle
    )

    return response_model


@router.post(
    "/facility/{facility}/cycles/current",
    response_model=FacilityCurrentOperatingCycleResponseModel,
    dependencies=[Depends(validate_admin_role)],
)
async def set_current_operating_cycle(
    facility: FacilityName,
    cycle: str,
):
    try:
        await facility_service.set_current_operating_cycle(facility, cycle)
    except CycleNotFoundError:
        # The requested cycle does not exist
        error_message = f"Cycle {cycle} not found for facility {facility.name}"
        logger.error(error_message)
        return fastapi.responses.JSONResponse(
            {"error": error_message}, status_code=fastapi.status.HTTP_400_BAD_REQUEST
        )
    except CycleVerificationError:
        # The verification of the cycle failed
        error_message = (
            f"Cycle {cycle} verification failed for facility {facility.name}"
        )
        logger.error(error_message)
        return fastapi.responses.JSONResponse(
            {"error": error_message}, status_code=fastapi.status.HTTP_400_BAD_REQUEST
        )
    except CycleUpdateError as e:
        # Handle update failure with access to the reason
        logger.error(f"Cycle update failed: {e.reason}")
        return fastapi.responses.JSONResponse(
            {"error": "Cycle Update failed"},
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        )
    except CycleOperationError:
        # Catch-all for any other errors that may occur
        logger.error("Cycle Update failed")
        return fastapi.responses.JSONResponse(
            {"error": "Cycle Update failed"},
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response_model = FacilityCurrentOperatingCycleResponseModel(
        facility=facility.name, cycle=cycle
    )

    return response_model


@router.get(
    "/facility/{facility}/cycles",
    response_model=FacilityCyclesResponseModel,
    include_in_schema=True,
)
async def get_facility_cycles(facility: FacilityName):
    cycle_list = await facility_service.facility_cycles(facility.name)
    if cycle_list is None:
        return fastapi.responses.JSONResponse(
            {"error": f"No cycles were found for facility {facility.name}"},
            status_code=404,
        )
    response_model = FacilityCyclesResponseModel(
        facility=facility.name, cycles=cycle_list
    )
    return response_model


@router.get(
    "/facility/{facility}/cycle/{cycle}/proposals",
    response_model=CycleProposalList,
    include_in_schema=True,
)
async def get_proposals_for_cycle(facility: FacilityName, cycle: str):
    proposal_list = await proposal_service.fetch_proposals_for_cycle(cycle, facility)
    if proposal_list is None:
        return fastapi.responses.JSONResponse(
            {
                "error": f"No proposals were found for cycle {cycle} for facility {facility.name}"
            },
            status_code=404,
        )
    model = CycleProposalList(
        cycle=cycle, proposals=proposal_list, count=len(proposal_list)
    )
    return model


@router.get(
    "/facility/{facility}/cycle_by_date",
    response_model=FacilityCycleResponseModel,
    include_in_schema=True,
)
async def get_cycle_by_date(facility: FacilityName, date: str):
    """
        Get the facility cycle that covers a specific date.

        Args:
            facility (FacilityName): The facility identifier (e.g., "nsls2").
            date (str): The date to query in ISO format (YYYY-MM-DD).

        Returns:
            FacilityCycleResponseModel: The cycle covering the given date, including whether it is the current operating cycle.

        Responses:
            200: Cycle found for the given date.
            400: Invalid date format.
            404: No cycle found for the given date.
    """
    try:
        query_date = datetime.fromisoformat(date)
    except ValueError:
        return fastapi.responses.JSONResponse(
            {"error": f"Invalid date format: {date}. Use YYYY-MM-DD."},
            status_code=400,
        )

    found_cycle = await facility_service.facility_cycle_by_date(facility.name, query_date)
    if not found_cycle:
        return fastapi.responses.JSONResponse(
            {"error": f"No cycle found for date {date} in facility {facility.name}"},
            status_code=404,
        )

    model = FacilityCycleResponseModel(
        facility=facility.name,
        cycle=found_cycle.name,
        start_date=found_cycle.start_date.isoformat() if found_cycle.start_date else None,
        end_date=found_cycle.end_date.isoformat() if found_cycle.end_date else None,
        is_current_operating_cycle=found_cycle.is_current_operating_cycle,
        active=found_cycle.active,
    )
    return model


@router.post(
    "/facility/{facility}/cycles/set_current_cycle_by_today",
    response_model=FacilityCycleResponseModel,
    include_in_schema=True,
    dependencies=[Depends(validate_admin_role)],
)
async def set_current_cycle_by_today(facility: FacilityName):
    """
        Set the current operating cycle for a facility to the cycle covering today's date.

        This admin-only endpoint finds the cycle that covers the current UTC date and sets it as the current operating cycle for the given facility.

        Args:
            facility (FacilityName): The facility identifier (e.g., "nsls2").

        Returns:
            FacilityCycleResponseModel: The updated cycle, now set as the current operating cycle.

        Responses:
            200: The current cycle was successfully updated.
            404: No cycle found covering today's date for the facility.
            403: Not authorized (admin only).
    """
    today = datetime.now(timezone.utc)
    print(today)
    found_cycle = await facility_service.facility_cycle_by_date(facility.name, today)
    if not found_cycle:
        return fastapi.responses.JSONResponse(
            {"error": f"No cycle found for today's date in facility {facility.name}"},
            status_code=404,
        )
    await facility_service.set_current_operating_cycle(facility.name, found_cycle.name)
    model = FacilityCycleResponseModel(
        facility=facility.name,
        cycle=found_cycle.name,
        start_date=found_cycle.start_date.isoformat() if found_cycle.start_date else None,
        end_date=found_cycle.end_date.isoformat() if found_cycle.end_date else None,
        is_current_operating_cycle=True,
        active=found_cycle.active,
    )
    return model