from N2SNUserTools.ldap import ADObjects
from typing import Optional
import pydantic
import asyncer

class ActiveDirectoryUser(pydantic.BaseModel):
    sAMAccountName: Optional[str] = None
    distinguishedName: Optional[str] = None
    displayName: Optional[str] = None
    employeeID: Optional[str] = None
    mail: Optional[str] = None
    description: Optional[str] = None
    userPrincipalName: Optional[str] = None
    pwdLastSet: Optional[str] = None
    userAccountControl: Optional[str] = None
    lockoutTime: Optional[str] = None
    set_passwd: Optional[bool] = None
    locked: Optional[bool] = None
    was_locked: Optional[bool] = None

def get_users_in_group(group: str) -> list[ActiveDirectoryUser]:
    """
    :param group: The name of the group that you want to retrieve the users from.
    :param settings: The settings used to connect to the Active Directory server. Defaults to the settings defined in the `get_settings` method.

    :return: A list of `ActiveDirectoryUser` objects representing the users in the specified group.

    """
    with ADObjects(
        "dc2.bnl.gov",
        user_search='ou=cam - users,ou=cam,dc=bnl,dc=gov',
        group_search='dc=bnl,dc=gov',
        authenticate=False,
        ca_certs_file="/etc/pki/ca-trust/source/anchors/bnlroot.crt"
    ) as ad:
        users = ad.get_group_members(group)

    return users

async def get_users_in_group_async(group: str) -> list[ActiveDirectoryUser]:
    """
    :param group: The name of the group that you want to retrieve the users from.
    :param settings: The settings used to connect to the Active Directory server. Defaults to the settings defined in the `get_settings` method.

    :return: A list of `ActiveDirectoryUser` objects representing the users in the specified group.

    """
    with ADObjects(
        "dc2.bnl.gov",
        user_search='ou=cam - users,ou=cam,dc=bnl,dc=gov',
        group_search='dc=bnl,dc=gov',
        authenticate=False,
        ca_certs_file="/etc/pki/ca-trust/source/anchors/bnlroot.crt"
    ) as ad:
        users = ad.get_group_members(group)

    return users


a=get_users_in_group("nsls2-dataadmin")
b=asyncer.runnify(get_users_in_group_async)(group="nsls2-dataadmin")
