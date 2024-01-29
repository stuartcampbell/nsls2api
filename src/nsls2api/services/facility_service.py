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
