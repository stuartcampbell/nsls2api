from pathlib import Path
from typing import Optional

from nsls2api.models.beamlines import (
    Beamline,
    ServicesOnly,
    ServiceAccounts,
    ServiceAccountsView,
    WorkflowServiceAccountView,
    IOCServiceAccountView,
    EpicsServicesServiceAccountView,
    BlueskyServiceAccountView,
    OperatorServiceAccountView,
    DataRootDirectoryView, LsdcServiceAccountView,
)


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


async def all_services(name: str) -> Optional[ServicesOnly]:
    beamline_services = await Beamline.find_one(Beamline.name == name.upper()).project(
        ServicesOnly
    )
    return beamline_services.services


async def service_accounts(name: str) -> Optional[ServiceAccounts]:
    accounts = await Beamline.find_one(Beamline.name == name.upper()).project(
        ServiceAccountsView
    )
    return accounts.service_accounts

async def data_root_directory(name: str) -> str:
    default_root = Path("/nsls2/data")

    data_root = await Beamline.find_one(Beamline.name == name.upper()).project(
        DataRootDirectoryView
    )

    # print(f"data_root: {data_root} ")

    if data_root.data_root is None:
        data_root_prefix = default_root / name.lower()
    else:
        data_root_prefix = default_root / data_root.data_root
    return data_root_prefix

# TODO: Not sure if I really need any of the following methods, or just use the generic `service_accounts()` above.

async def workflow_username(name: str) -> str:
    workflow_account = await Beamline.find_one(Beamline.name == name.upper()).project(
        WorkflowServiceAccountView
    )
    return workflow_account.username


async def ioc_username(name: str) -> str:
    ioc_account = await Beamline.find_one(Beamline.name == name.upper()).project(
        IOCServiceAccountView
    )
    return ioc_account.username


async def bluesky_username(name: str) -> str:
    bluesky_account = await Beamline.find_one(Beamline.name == name.upper()).project(
        BlueskyServiceAccountView
    )
    return bluesky_account.username


async def operator_username(name: str) -> str:
    operator_account = await Beamline.find_one(Beamline.name == name.upper()).project(
        OperatorServiceAccountView
    )
    return operator_account.username


async def epics_services_username(name: str) -> str:
    epics_services_account = await Beamline.find_one(
        Beamline.name == name.upper()
    ).project(EpicsServicesServiceAccountView)
    return epics_services_account.username


async def lsdc_username(name: str) -> str:
    lsdc_account = await Beamline.find_one(
        Beamline.name == name.upper()
    ).project(LsdcServiceAccountView)
    return False if lsdc_account is None else lsdc_account.username
