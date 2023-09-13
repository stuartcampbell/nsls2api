from typing import Optional

from N2SNUserTools.ldap import ADObjects

from nsls2api.api.models.person_model import (
    ActiveDirectoryUser,
    ActiveDirectoryUserGroups,
)
from nsls2api.infrastructure import settings


async def get_groups_by_username(username: str) -> Optional[ActiveDirectoryUserGroups]:
    with ADObjects(
        settings.ACTIVE_DIRECTORY_SERVER,
        user_search=settings.N2SN_USER_SEARCH,
        group_search=settings.N2SN_GROUP_SEARCH,
        authenticate=False,
        ca_certs_file=settings.BNLROOT_CA_CERTS_FILE,
    ) as ad:
        user_details = ad.get_group_by_samaccountname(username)
    if len(user_details) == 0 or len(user_details) > 1:
        return None
    return ActiveDirectoryUserGroups(**user_details[0])


async def get_user_by_username(username: str) -> Optional[ActiveDirectoryUser]:
    with ADObjects(
        settings.ACTIVE_DIRECTORY_SERVER,
        user_search=settings.N2SN_USER_SEARCH,
        group_search=settings.N2SN_GROUP_SEARCH,
        authenticate=False,
        ca_certs_file=settings.BNLROOT_CA_CERTS_FILE,
    ) as ad:
        user_details = ad.get_user_by_samaccountname(username)
    if len(user_details) == 0 or len(user_details) > 1:
        return None
    return ActiveDirectoryUser(**user_details[0])


async def get_user_by_id(bnl_id: str) -> ActiveDirectoryUser:
    with ADObjects(
        settings.ACTIVE_DIRECTORY_SERVER,
        user_search=settings.N2SN_USER_SEARCH,
        group_search=settings.N2SN_GROUP_SEARCH,
        authenticate=False,
        ca_certs_file=settings.BNLROOT_CA_CERTS_FILE,
    ) as ad:
        user_details = ad.get_user_by_id(bnl_id)
    return ActiveDirectoryUser(**user_details[0])


async def get_users_in_group(group: str):
    with ADObjects(
        settings.ACTIVE_DIRECTORY_SERVER,
        user_search=settings.N2SN_USER_SEARCH,
        group_search=settings.N2SN_GROUP_SEARCH,
        authenticate=False,
        ca_certs_file=settings.BNLROOT_CA_CERTS_FILE,
    ) as ad:
        users = ad.get_group_members(group)
    return users


async def is_user_in_group(username: str, group: str):
    """
    Checks if a user is present in a specified group.

    Args:
        username (str): The username of the user to check.
        group (str): The name of the group to check.

    Returns:
        bool: True if the user is found in the group, False otherwise.
    """
    _user_found = False
    users = await get_users_in_group_async(group)
    _user_found: bool = any(
        [user for user in users if user["sAMAccountName"] == username]
    )
    return _user_found
