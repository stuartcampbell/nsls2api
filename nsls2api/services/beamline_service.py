from typing import Optional

from nsls2api.models.beamlines import Beamline, BeamlineService, ServicesOnly


async def beamline_count() -> int:
    """
    Returns the number of beamlines in the database.

    :return: An integer representing the number of beamlines in the database.
    """
    return await Beamline.count()


async def beamline_by_name(name: str) -> Optional[Beamline]:
    """
    Find and return a beamline by its name.

    :param name: The name of the beamline to search for.
    :return: The found beamline, if any. Otherwise, returns None.
    """
    # TODO: check that the input name looks sensible
    beamline = await Beamline.find_one(Beamline.name == name.upper())
    return beamline

async def all_services(name: str) -> Optional[list[BeamlineService]]:
    services = await Beamline.find_one(Beamline.name == name.upper()).project(ServicesOnly)
    return services
