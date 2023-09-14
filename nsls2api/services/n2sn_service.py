from typing import Optional

from N2SNUserTools.ldap import ADObjects
from fastapi import Depends

from nsls2api.api.models.person_model import (
    ActiveDirectoryUser,
    ActiveDirectoryUserGroups,
)
from ..infrastructure.config import get_settings


async def get_groups_by_username(username: str, settings=Depends(get_settings)) -> Optional[ActiveDirectoryUserGroups]:
    """
    :param username: The username for which you want to retrieve the groups.
    :param settings: Optional dependency on the application settings.
    :return: An instance of ActiveDirectoryUserGroups that contains information about the groups the user belongs to. Returns None if the user is not found or if there are multiple users with the same username.
    """
    with ADObjects(
            settings.active_directory_server,
            user_search=settings.n2sn_user_search,
            group_search=settings.n2sn_group_search,
            authenticate=False,
            ca_certs_file=settings.bnlroot_ca_certs_file,
    ) as ad:
        user_details = ad.get_group_by_samaccountname(username)
    if len(user_details) == 0 or len(user_details) > 1:
        return None
    return ActiveDirectoryUserGroups(**user_details[0])


async def get_user_by_username(username: str, settings=Depends(get_settings)) -> Optional[ActiveDirectoryUser]:
    """
    Get a user by their username.

    :param username: The username of the user.
    :param settings: Dependency of the application settings.
    :return: An instance of ActiveDirectoryUser if the user is found, else None.
    """
    with ADObjects(
            settings.active_directory_server,
            user_search=settings.n2sn_user_search,
            group_search=settings.n2sn_group_search,
            authenticate=False,
            ca_certs_file=settings.bnlroot_ca_certs_file,
    ) as ad:
        user_details = ad.get_user_by_samaccountname(username)
    if len(user_details) == 0 or len(user_details) > 1:
        return None
    return ActiveDirectoryUser(**user_details[0])


async def get_user_by_id(bnl_id: str, settings=Depends(get_settings)) -> ActiveDirectoryUser:
    """
    :param bnl_id: The BNL ID of the user to retrieve
    :param settings: The settings object to use for connecting to the AD server (default: Depends(get_settings))
    :return: An ActiveDirectoryUser object representing the user's details

    """
    with ADObjects(
            settings.active_directory_server,
            user_search=settings.n2sn_user_search,
            group_search=settings.n2sn_group_search,
            authenticate=False,
            ca_certs_file=settings.bnlroot_ca_certs_file,
    ) as ad:
        user_details = ad.get_user_by_id(bnl_id)
    return ActiveDirectoryUser(**user_details[0])


async def get_users_in_group(group: str, settings=Depends(get_settings)):
    """
    :param group: The name of the group that you want to retrieve the users from.
    :param settings: The settings used to connect to the Active Directory server. Defaults to the settings defined in the `get_settings` method.

    :return: A list of `ActiveDirectoryUser` objects representing the users in the specified group.

    """
    with ADObjects(
            settings.active_directory_server,
            user_search=settings.n2sn_user_search,
            group_search=settings.n2sn_group_search,
            authenticate=False,
            ca_certs_file=settings.bnlroot_ca_certs_file,
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
    users = await get_users_in_group(group)
    _user_found: bool = any(
        [user for user in users if user["sAMAccountName"] == username]
    )
    return _user_found
