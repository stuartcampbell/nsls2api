from nsls2api.infrastructure.logging import logger

from typing import Optional

from beanie.odm.operators.find.comparison import In

from nsls2api.models.cycles import Cycle
from nsls2api.models.facilities import Facility



async def facilities_count() -> int:
    """
    Count the number of facilities in the database.

    :return: The number of facilities.
    """
    return await Facility.count()


async def facility_cycles(facility: str) -> Optional[list[str]]:
    """
    Facility Cycles

    This method retrieves the cycles for a given facility.

    :param facility: The facility name (str).
    :return: A list of cycles for the facility (list[Cycle]).
    """
    cycles = await Cycle.find(Cycle.facility == facility).to_list()
    cycle_list = [c.name for c in cycles if c.name is not None]
    return cycle_list


async def data_roles_by_user(username: str) -> Optional[list[str]]:
    facilities = await Facility.find(In(Facility.data_admins, [username])).to_list()
    facility_names = [f.facility_id for f in facilities if f.facility_id is not None]
    return facility_names


async def current_operating_cycle(facility: str) -> Optional[str]:
    """
    Current Operating Cycle

    This method retrieves the current operating cycle for a given facility.

    :param facility: The facility name (str).
    :return: The current operating cycle (str) or None if no current operating cycle is found.
    """
    cycle = await Cycle.find_one(
        Cycle.facility == facility,
        Cycle.is_current_operating_cycle == True,  # noqa: E712
    )

    if cycle is None:
        return None
    
    return cycle.name

  
async def is_healthy(facility: str) -> bool:
    """
    Database Health Check

    This method checks the health of the information in the database.
    Basically, is the database populated with the correct information?
    e.g. Is there only one current operating cycle for a facility?

    :param facility: The facility name (str).
    :return: True if the database is healthy, False otherwise.
    """

    # Let's start with assuming the database is healthy.
    health_status = True

    logger.info(f"Checking the health of the {facility} facility data.")

    # TODO: Check that the facility exists in the database.


    # Check that there is only one current operating cycle for the facility.
    cycles = await Cycle.find(Cycle.is_current_operating_cycle == facility).to_list()
    if len(cycles) > 1:
        logger.warning(
            f"There is more than one current operating cycle for the {facility}."
        )
        health_status = False
    elif len(cycles) == 0:
        logger.warning(f"There is not an operating cycle for the {facility}.")
        health_status = False
    
    return health_status

