import datetime
from pathlib import Path
from typing import Optional

from beanie.odm.operators.find.comparison import In
from beanie.odm.operators.find.array import ElemMatch

from nsls2api.models.beamlines import AssetDirectoryGranularity
from nsls2api.infrastructure.logging import logger
from nsls2api.models.beamlines import (
    Beamline,
    BeamlineService,
    Detector,
    DetectorView,
    ServicesOnly,
    ServiceAccounts,
    ServiceAccountsView,
    SlackChannelManagersView,
    WorkflowServiceAccountView,
    IOCServiceAccountView,
    EpicsServicesServiceAccountView,
    BlueskyServiceAccountView,
    OperatorServiceAccountView,
    DataRootDirectoryView,
    LsdcServiceAccountView,
)
from nsls2api.services import slack_service


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


async def beamline_by_pass_id(pass_id: str) -> Optional[Beamline]:
    """
    Find and return a beamline by its PASS ID.

    :param pass_id: The PASS ID of the beamline to search for.
    :return: The found beamline, if any. Otherwise, returns None.
    """
    beamline = await Beamline.find_one(Beamline.pass_id == str(pass_id))
    return beamline


async def all_services(name: str) -> Optional[ServicesOnly]:
    beamline_services = await Beamline.find_one(Beamline.name == name.upper()).project(
        ServicesOnly
    )
    return beamline_services.services


async def detectors(name: str) -> Optional[list[Detector]]:
    detectors = await Beamline.find_one(Beamline.name == name.upper()).project(
        DetectorView
    )

    if detectors is None:
        return None

    return detectors.detectors


async def service_accounts(name: str) -> Optional[ServiceAccounts]:
    accounts = await Beamline.find_one(Beamline.name == name.upper()).project(
        ServiceAccountsView
    )

    if accounts is None:
        return None

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
    if workflow_account is None:
        # Let's make an educated guess
        return f"workflow-{name.lower()}"
    return workflow_account.username


async def ioc_username(name: str) -> str:
    ioc_account = await Beamline.find_one(Beamline.name == name.upper()).project(
        IOCServiceAccountView
    )
    if ioc_account is None:
        # Let's make an educated guess
        return f"softioc-{name.lower()}"

    return ioc_account.username


async def bluesky_username(name: str) -> str:
    bluesky_account = await Beamline.find_one(Beamline.name == name.upper()).project(
        BlueskyServiceAccountView
    )
    if bluesky_account is None:
        # Let's make an educated guess
        return f"bluesky-{name.lower()}"

    return bluesky_account.username


async def operator_username(name: str) -> str:
    operator_account = await Beamline.find_one(Beamline.name == name.upper()).project(
        OperatorServiceAccountView
    )

    if operator_account is None:
        raise LookupError(
            f"Could not find a the operator account for the {name} beamline."
        )

    return operator_account.username


async def epics_services_username(name: str) -> str:
    epics_services_account = await Beamline.find_one(
        Beamline.name == name.upper()
    ).project(EpicsServicesServiceAccountView)

    if epics_services_account is None:
        # Let's make an educated guess
        return f"epics-services-{name.lower()}"

    return epics_services_account.username


async def lsdc_username(name: str) -> Optional[str]:
    lsdc_account = await Beamline.find_one(Beamline.name == name.upper()).project(
        LsdcServiceAccountView
    )

    if lsdc_account is None:
        return None

    return lsdc_account.username


async def data_roles_by_user(username: str) -> Optional[list[str]]:
    beamlines = await Beamline.find(In(Beamline.data_admins, [username])).to_list()
    beamline_names = [b.name.lower() for b in beamlines if b.name is not None]
    return beamline_names


async def custom_data_admin_group(name: str) -> str:
    beamline = await Beamline.find_one(Beamline.name == name.upper())

    if beamline.custom_data_admin_group is None:
        return f"n2sn-right-dataadmin-{name.lower()}"
    else:
        return beamline.custom_data_admin_group


async def proposal_directory_skeleton(name: str):
    detector_list = await detectors(name.upper())

    directory_list = []

    # TODO: Make this parameter configurable (i.e. have field in beamline document model for this value)
    asset_directory_name = "assets"

    users_acl: list[dict[str, str]] = []
    groups_acl: list[dict[str, str]] = []

    service_usernames = await service_accounts(name)

    if service_usernames.ioc is not None:
        users_acl.append({f"{service_usernames.ioc}": "rw"})
    
    users_acl.append({"softioc": "rw"})
    
    if service_usernames.bluesky is not None:
        users_acl.append({f"{service_usernames.bluesky}": "rw"})

    if service_usernames.workflow is not None:
        users_acl.append({f"{service_usernames.workflow}": "r"})
    
    users_acl.append({"nsls2data": "rw"})

    groups_acl.append({f"{await custom_data_admin_group(name)}": "r"})
    groups_acl.append({"n2sn-right-dataadmin": "r"})

    # Add the asset directory so this has the same permissions as the detector directories
    # and not just inherit from the parent (i.e. proposal) directory.
    asset_directory = {
        "path": f"{asset_directory_name}",
        "is_absolute": False,
        "owner": "nsls2data",
        "users": users_acl,
        "groups": groups_acl,
        "beamline": name.upper(),
    }
    directory_list.append(asset_directory)

    # Add the detector subdirectories
    if detector_list:
        for detector in detector_list:
            directory = {
                "path": f"{asset_directory_name}/{detector.directory_name}",
                "is_absolute": False,
                "owner": "nsls2data",
                "users": users_acl,
                "groups": groups_acl,
                "beamline": name.upper(),
                "directory_most_granular_level": detector.granularity,
            }
            directory_list.append(directory)

    # Add a default directory for non-named detectors
    default_directory = {
        "path": f"{asset_directory_name}/default",
        "is_absolute": False,
        "owner": "nsls2data",
        "users": users_acl,
        "groups": groups_acl,
        "beamline": name.upper(),
        "directory_most_granular_level": AssetDirectoryGranularity.day,
    }
    directory_list.append(default_directory)

    return directory_list


async def check_service_exists(beamline_name: str, service_name: str) -> bool:
    """
    Check if a service exists in a given beamline.

    Args:
        beamline_name (str): The name of the beamline.
        service_name (str): The name of the service.

    Returns:
        bool: True if the service exists in the beamline, False otherwise.
    """

    # Get the beamline from the database
    beamline = await Beamline.find_one(Beamline.name == beamline_name.upper())

    # If the beamline does not exist, then by definition it can't have the service
    if beamline is None:
        return False

    current_services = await beamline.find(
        ElemMatch(Beamline.services, {"name": service_name})
    ).to_list()

    print(f"current_services: {current_services}")

    if current_services is None or len(current_services) == 0:
        logger.info(f"Service {service_name} not found in beamline {beamline_name}")
        return False
    else:
        logger.info(f"Service {service_name} found in beamline {beamline_name}")
        return True

    return False


async def add_service(
    beamline_name: str,
    service_name: str,
    used_in_production: bool = False,
    host: str = None,
    port: int = None,
    uri: str = None,
) -> Optional[BeamlineService]:
    """
    Add a new service to a beamline.

    Args:
        beamline_name (str): The name of the beamline.
        service_name (str): The name of the service.
        used_in_production (bool, optional): Whether the service is used in production. Defaults to False.
        host (str, optional): The host of the service. Defaults to None.
        port (int, optional): The port of the service. Defaults to None.
        uri (str, optional): The URI of the service. Defaults to None.

    Returns:
        Optional[BeamlineService]: The newly created BeamlineService object if successful, None otherwise.
    """
    beamline = await Beamline.find_one(Beamline.name == beamline_name.upper())

    service = BeamlineService(
        name=service_name,
        used_in_production=used_in_production,
        host=host,
        port=port,
        uri=uri,
    )

    if await check_service_exists(beamline_name, service_name):
        logger.info(
            f"Service {service_name} already exists in beamline {beamline_name}"
        )
        return None
    else:
        beamline.services.append(service)
        beamline.last_updated = datetime.datetime.now()
        await beamline.save()

    return service


async def uses_synchweb(name: str) -> bool:
    """
    Check if the specified beamline uses the SynchWeb service.

    Args:
        name (str): The name of the beamline.

    Returns:
        bool: True if the beamline uses SynchWeb, False otherwise.
    """
    if await check_service_exists(name, "synchweb"):
        return True
    else:
        return False


async def slack_channel_managers(beamline_name: str) -> list[str]:
    """
    Retrieves the Slack user IDs of the channel managers for a given beamline.

    Args:
        beamline_name (str): The name of the beamline.

    Returns:
        list[str]: A list of Slack user IDs of the channel managers.

    """
    beamline = await Beamline.find_one(Beamline.name == beamline_name.upper()).project(
        SlackChannelManagersView
    )
    if beamline is None:
        return None

    slack_ids = []
    for user in beamline.slack_channel_managers:
        # Staff have to have a BNL email account
        email = f"{user}@bnl.gov"
        user_id = slack_service.lookup_userid_by_email(email=email)
        if user_id:
            slack_ids.append(user_id)

    return slack_ids
