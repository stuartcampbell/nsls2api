from typing import Optional

from pydantic import ValidationError
from nsls2api.api.models.facility_model import FacilityName, UpsFacilityName
from nsls2api.models.proposals import User
from nsls2api.models.universalproposal_models import (
    UpsCycle,
    UpsProposalType,
    UpsProposalRecord,
    UpsUser,
)
from nsls2api.infrastructure.config import get_settings
from nsls2api.infrastructure.logging import logger

from nsls2api.services import bnlpeople_service, facility_service
from nsls2api.services.helpers import _call_async_webservice_with_client
from nsls2api.infrastructure.app_setup import httpx_client_wrapper

settings = get_settings()

base_url = settings.universal_proposal_system_api_url
username = settings.universal_proposal_system_api_user
password = settings.universal_proposal_system_api_password


class UniversalProposalSystemException(Exception):
    pass


async def _call_ups_servicenow_webservice(url: str):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    return await _call_async_webservice_with_client(
        url, auth=(username, password), headers=headers, client=httpx_client_wrapper()
    )


async def get_raw_proposal_types(
    facility: UpsFacilityName = UpsFacilityName.nsls2,
):
    ups_facility_id = await facility_service.ups_id_for_facility(facility_name=facility)

    if not ups_facility_id:
        error_message: str = (
            f"Facility {facility} does not have a Universal Proposal System ID."
        )
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message)

    url = f"{base_url}/now/table/sn_customerservice_proposal_type?sysparm_query=u_facility={ups_facility_id}&sysparm_display_value=all"

    ups_proposal_types_list = await _call_ups_servicenow_webservice(url)

    logger.info(f"UPS Returned {len(ups_proposal_types_list)} proposal types.")

    return ups_proposal_types_list["result"]


async def get_facility_details(
    facility: UpsFacilityName = UpsFacilityName.nsls2,
):
    ups_facility_id = await facility_service.ups_id_for_facility(facility_name=facility)

    if not ups_facility_id:
        error_message: str = (
            f"Facility {facility} does not have a Universal Proposal System ID."
        )
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message)

    url = f"{base_url}/now/table/cmn_location/{ups_facility_id}"

    ups_facility_info = await _call_ups_servicenow_webservice(url)

    return ups_facility_info["result"]


async def get_all_facility_details():
    url = f"{base_url}/now/table/cmn_location?sysparm_display_value=all"

    ups_facility_info = await _call_ups_servicenow_webservice(url)

    return ups_facility_info["result"]


async def get_raw_proposal(proposal_id: str):
    url = f"{base_url}/now/table/sn_customerservice_proposal_record?sysparm_query=u_proposal_number%3D{proposal_id}&sysparm_display_value=all"

    ups_proposal = await _call_ups_servicenow_webservice(url)

    return ups_proposal["result"]


async def get_proposal_types(
    facility: UpsFacilityName = UpsFacilityName.nsls2,
) -> list[UpsProposalType]:
    ups_facility_id = await facility_service.ups_id_for_facility(facility_name=facility)

    if not ups_facility_id:
        error_message: str = (
            f"Facility {facility} does not have a Universal Proposal System ID."
        )
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message)

    url = f"{base_url}/now/table/sn_customerservice_proposal_type?sysparm_query=u_facility={ups_facility_id}&sysparm_display_value=all"

    try:
        ups_proposal_types_list_response = await _call_ups_servicenow_webservice(url)
        ups_proposal_types_list = ups_proposal_types_list_response["result"]
        proposal_types = []
        if ups_proposal_types_list and len(ups_proposal_types_list) > 0:
            for proposal_type in ups_proposal_types_list:
                proposal_types.append(UpsProposalType(**proposal_type))
    except ValidationError as error:
        error_message = f"Error validating data recevied from UPS for proposal type for the {facility} facility."
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message) from error
    except Exception as error:
        error_message = (
            "Error retrieving proposal types from the Universal Proposal System."
        )
        logger.exception(error_message)
        raise UniversalProposalSystemException(error_message) from error

    return proposal_types


async def get_proposal(proposal_id: str) -> Optional[UpsProposalRecord]:
    proposal_query = proposal_id.strip()
    # TODO: Maybe do a regex check here to make sure the proposal_query is in the correct format.

    servicenow_table_name = "sn_customerservice_proposal_record"
    url = f"{base_url}/now/table/{servicenow_table_name}?sysparm_query=u_proposal_number%3D{proposal_query}&sysparm_display_value=all"

    try:
        ups_proposal_response = await _call_ups_servicenow_webservice(url)

        # Did we get anything back ?
        if (
            not ups_proposal_response["result"]
            or len(ups_proposal_response["result"]) == 0
        ):
            return None

        # We aren't going to handle multiple proposals, so just throw an error if we get more than one.
        if len(ups_proposal_response["result"]) > 1:
            error_message = (
                f"UPS returned more than one proposal for proposal {proposal_id}."
            )
            logger.error(error_message)
            raise UniversalProposalSystemException(error_message)

        ups_proposal = ups_proposal_response["result"][0]
        proposal = UpsProposalRecord(**ups_proposal)
    except ValidationError as error:
        error_message = (
            f"Error validating data recevied from UPS for proposal {proposal_id}."
        )
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message) from error
    except Exception as error:
        error_message = f"Error retrieving proposal {proposal_id} from UPS. {error}"
        logger.exception(error_message)
        raise UniversalProposalSystemException(error_message) from error

    return proposal


async def get_all_proposals_for_facility(
    facility: FacilityName = FacilityName.nsls2,
) -> Optional[list[UpsProposalRecord]]:
    # First check we have the details for the facility we need.
    ups_facility_id = await facility_service.ups_id_for_facility(facility_name=facility)
    if not ups_facility_id:
        error_message: str = (
            f"Facility {facility} does not have a Universal Proposal System ID."
        )
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message)

    # Get a list of proposal types for the given facility
    proposal_types = await get_proposal_types(facility=facility)

    if not proposal_types or len(proposal_types) == 0:
        error_message: str = (
            f"Facility {facility} does not have any proposal types within the UPS."
        )
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message)

    facility_proposal_list = []

    servicenow_table_name = "sn_customerservice_proposal_record"

    for proposal_type in proposal_types:
        query = f"u_proposal_type%3D{proposal_type.sys_id.value}"
        url = f"{base_url}/now/table/{servicenow_table_name}?sysparm_query={query}&sysparm_display_value=all"

        try:
            ups_proposal_response = await _call_ups_servicenow_webservice(url)
            ups_proposals = ups_proposal_response["result"]
            if ups_proposals and len(ups_proposals) > 0:
                logger.info(
                    f"Found {len(ups_proposals)} proposals for proposal type {proposal_type.u_name.value}."
                )
                for ups_proposal in ups_proposals:
                    # logger.info(f"Validating proposal {ups_proposal['u_proposal_number']}.")
                    facility_proposal_list.append(UpsProposalRecord(**ups_proposal))
        except ValidationError as error:
            error_message = f"Error validating data recevied from UPS for all proposals from {facility}."
            logger.error(error_message)
            raise UniversalProposalSystemException(error_message) from error
        except Exception as error:
            error_message = f"Error retrieving proposals from UPS. {error}"
            logger.exception(error_message)
            raise UniversalProposalSystemException(error_message) from error

    return facility_proposal_list


async def get_cycles(
    facility: FacilityName = FacilityName.nsls2,
) -> Optional[list[UpsCycle]]:
    ups_facility_id = await facility_service.ups_id_for_facility(facility_name=facility)

    if not ups_facility_id:
        error_message: str = (
            f"Facility {facility} does not have a Universal Proposal System ID."
        )
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message)

    servicenow_table_name = "sn_customerservice_run_cycle"
    url = f"{base_url}/now/table/{servicenow_table_name}?sysparm_query=u_facility={ups_facility_id}&sysparm_display_value=all"

    logger.info(f"Getting cycles from UPS for {facility} facility.")

    try:
        ups_cycle_list_response = await _call_ups_servicenow_webservice(url)
        ups_cycle_list = ups_cycle_list_response["result"]
        cycles = []
        if ups_cycle_list and len(ups_cycle_list) > 0:
            for ups_cycle in ups_cycle_list:
                cycles.append(UpsCycle(**ups_cycle))
    except ValidationError as error:
        error_message = f"Error validating cycle data recevied from UPS for the {facility} facility."
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message) from error
    except Exception as error:
        error_message = "Error retrieving cycle information from UPS."
        logger.exception(error_message)
        raise UniversalProposalSystemException(error_message) from error

    return cycles


async def get_user(user_ups_id: str) -> Optional[UpsUser]:
    servicenow_table_name = "sys_user"
    url = f"{base_url}/now/table/{servicenow_table_name}?sysparm_query=sys_id={user_ups_id}&sysparm_display_value=all"

    user = None

    try:
        ups_user_response = await _call_ups_servicenow_webservice(url)
        raw_user = ups_user_response["result"]
        if raw_user and len(raw_user) > 0:
            user = UpsUser(**raw_user[0])
    except ValidationError as error:
        error_message = f"Error validating user data recevied from UPS for user sys_id = {user_ups_id}."
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message) from error
    except Exception as error:
        error_message = "Error retrieving user information from UPS."
        logger.exception(error_message)
        raise UniversalProposalSystemException(error_message) from error

    return user


async def get_institution_info(institution_id: str):
    servicenow_table_name = "u_ror_data"


async def extract_users_from_proposal(proposal: UpsProposalRecord) -> list[User]:
    users = []

    # PI
    pi_users: list[str] = proposal.u_principal_investigator_pi.value.split(",")
    for pi_user in pi_users:
        user = await get_user(pi_user.strip())
        bnl_username = None
        if user:
            if (
                user.u_brookhaven_badge is not None
                and len(user.u_brookhaven_badge.display_value) > 0
            ):
                try:
                    bnl_username = await bnlpeople_service.get_username_by_id(
                        user.u_brookhaven_badge.display_value
                    )
                except LookupError:
                    logger.warning(
                        f"Could not find a BNL username for user with BNL ID: {user.u_brookhaven_badge}"
                    )

            if bnl_username is None:
                # Now lets try the email
                if user.email is not None and len(user.email.display_value) > 0:
                    try:
                        bnl_username = await bnlpeople_service.get_username_by_email(
                            user.email.display_value
                        )
                    except LookupError:
                        logger.warning(
                            f"Could not find a BNL username for user with email: {user.email.display_value}"
                        )

            users.append(
                User(
                    first_name=user.first_name.display_value,
                    last_name=user.last_name.display_value,
                    email=user.email.display_value,
                    username=bnl_username,
                    bnl_id=user.u_brookhaven_badge.display_value,
                    orcid=user.u_orcid.display_value,
                    is_pi=True,
                )
            )

    # Co-PIs
    co_proposers: list[str] = proposal.u_co_proposers.value.split(",")
    for person in co_proposers:
        user = await get_user(person.strip())
        bnl_username = None
        if user:
            if (
                user.u_brookhaven_badge is not None
                and len(user.u_brookhaven_badge.display_value) > 0
            ):
                try:
                    bnl_username = await bnlpeople_service.get_username_by_id(
                        user.u_brookhaven_badge.display_value
                    )
                except LookupError:
                    logger.warning(
                        f"Could not find a BNL username for user with BNL ID: {user.u_brookhaven_badge.display_value}"
                    )

            if bnl_username is None:
                # Now lets try the email
                if user.email is not None and len(user.email.display_value) > 0:
                    try:
                        bnl_username = await bnlpeople_service.get_username_by_email(
                            user.email.display_value
                        )
                    except LookupError:
                        logger.warning(
                            f"Could not find a BNL username for user with email: {user.email.display_value}"
                        )

            users.append(
                User(
                    first_name=user.first_name.display_value,
                    last_name=user.last_name.display_value,
                    email=user.email.display_value,
                    username=bnl_username,
                    bnl_id=user.u_brookhaven_badge.display_value,
                    orcid=user.u_orcid.display_value,
                    is_pi=False,
                )
            )

    # Contributors
    contributors: list[str] = proposal.u_contributor_users.value.split(",")
    for person in contributors:
        user = await get_user(person.strip())
        bnl_username = None
        if user:
            if (
                user.u_brookhaven_badge is not None
                and len(user.u_brookhaven_badge.display_value) > 0
            ):
                try:
                    bnl_username = await bnlpeople_service.get_username_by_id(
                        user.u_brookhaven_badge.display_value
                    )
                except LookupError:
                    logger.warning(
                        f"Could not find a BNL username for user with BNL ID: {user.u_brookhaven_badge.display_value}"
                    )

            if bnl_username is None:
                # Now lets try the email
                if user.email is not None and len(user.email.display_value) > 0:
                    try:
                        bnl_username = await bnlpeople_service.get_username_by_email(
                            user.email.display_value
                        )
                    except LookupError:
                        logger.warning(
                            f"Could not find a BNL username for user with email: {user.email.display_value}"
                        )

            users.append(
                User(
                    first_name=user.first_name.display_value,
                    last_name=user.last_name.display_value,
                    email=user.email.display_value,
                    username=bnl_username,
                    bnl_id=user.u_brookhaven_badge.display_value,
                    orcid=user.u_orcid.display_value,
                    is_pi=False,
                )
            )

    return users
