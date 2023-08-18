from typing import Optional

from nsls2api.models.beamlines import Beamline, BeamlineService, ServicesOnly, ServiceAccounts


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


async def workflow_username(name: str) -> str:
    service_accounts: ServiceAccounts = await Beamline.find_one(Beamline.name == name.upper()).project(ServiceAccounts)
    return service_accounts.workflow


async def ioc_username(name: str) -> str:
    service_accounts: ServiceAccounts = await Beamline.find_one(Beamline.name == name.upper()).project(ServiceAccounts)
    return service_accounts.ioc


async def bluesky_username(name: str) -> str:
    service_accounts: ServiceAccounts = await Beamline.find_one(Beamline.name == name.upper()).project(ServiceAccounts)
    return service_accounts.bluesky


async def operator_username(name: str) -> str:
    service_accounts: ServiceAccounts = await Beamline.find_one(Beamline.name == name.upper()).project(ServiceAccounts)
    return service_accounts.operator


async def epics_services_username(name: str) -> str:
    service_accounts: ServiceAccounts = await Beamline.find_one(Beamline.name == name.upper()).project(ServiceAccounts)
    return service_accounts.epics_services
