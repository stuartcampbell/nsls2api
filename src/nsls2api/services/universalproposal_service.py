from typing import Optional

from pydantic import ValidationError
from nsls2api.api.models.facility_model import FacilityName, UpsFacilityName
from nsls2api.models.proposals import User
from nsls2api.models.universalproposal_models import (
    UpsCycle,
    UpsExperimentTimeRequest,
    UpsProposalType,
    UpsProposalRecord,
    UpsRunCycleProposalMapping,
    UpsUser,
)
from nsls2api.infrastructure.config import get_settings
from nsls2api.infrastructure.logging import logger

from nsls2api.services import beamline_service, bnlpeople_service, facility_service, proposal_service
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

    if not proposal_id:
        return None


    # TODO: Maybe do a regex check here to make sure the proposal_query is in the correct format.

    servicenow_table_name = "sn_customerservice_proposal_record"
    query = f"u_proposal_number={proposal_id.strip()}"
    url = f"{base_url}/now/table/{servicenow_table_name}?sysparm_query={query}&sysparm_display_value=all"

    logger.info(url)

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

async def get_etr_for_proposal(proposal_id: str) -> Optional[str]:

    proposal_ups_sys_id = None

    try:
        proposal = await proposal_service.proposal_by_id(proposal_id)
        proposal_ups_sys_id = proposal.universal_proposal_system_id
    except LookupError:
        # If we haven't found the proposal in our local database, then ask the UPS
        proposal = await get_proposal(proposal_id)
        proposal_ups_sys_id = proposal.u_proposal_number.value

    servicenow_table_name = "sn_customerservice_experiment_time_request"
    query=f"u_proposal={proposal_ups_sys_id}"
    url = f"{base_url}/now/table/{servicenow_table_name}?sysparm_query={query}&sysparm_display_value=all"
    logger.info(url)
    etr_list = []

    try:
        ups_etr_list_response = await _call_ups_servicenow_webservice(url)
        ups_etr_list = ups_etr_list_response["result"]

        logger.info(f"Found {len(ups_etr_list)} ETRs for proposal {proposal_id}.")

        if ups_etr_list and len(ups_etr_list) > 0:
            for etr in ups_etr_list:
                etr_list.append(UpsExperimentTimeRequest(**etr))
    except ValidationError as error:
        error_message = f"Error validating data recevied from Universal Proposal System (UPS) for ETR corresponding to proposal {proposal_id}."
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message) from error
    except Exception as error:
        error_message = (
            f"Error retrieving ETR for proposal {proposal_id} from the Universal Proposal System (UPS)."
        )
        logger.exception(error_message)
        raise UniversalProposalSystemException(error_message) from error
    
    return etr_list

async def get_beamlines_from_proposal(proposal_id: str) -> list[str]:
    beamlines = []

    etr_list = await get_etr_for_proposal(proposal_id)
    if etr_list and len(etr_list) > 0:
        for etr in etr_list:
            logger.debug(f"Getting beamlines for ETR {etr.sys_id.value}.")
            beamline_one = await beamline_service.beamline_by_ups_id(etr.u_beamline_one.value)
            beamline_two = await beamline_service.beamline_by_ups_id(etr.u_beamline_two.value)
 
            if beamline_one:
                beamlines.append(beamline_one)
            else:
                # Only display a warning if we actually have anything
                if len(etr.u_beamline_one.display_value) > 0:
                    logger.warning(f"Could not find beamline name for UPS beamline (one) {etr.u_beamline_one.display_value}. ({etr.u_beamline_one.value})")
 
            if beamline_two:
                beamlines.append(beamline_two)
            else:
                # Only display a warning if we actually have anything
                if len(etr.u_beamline_two.display_value) > 0:
                    logger.warning(f"Could not find beamline name for UPS beamline (two) {etr.u_beamline_two.display_value}. ({etr.u_beamline_two.value})")
 
    return beamlines

async def get_cycle_by_name(cycle_name: str, facility: UpsFacilityName = UpsFacilityName.nsls2) -> Optional[UpsCycle]:
    """
    Retrieves a cycle from the Universal Proposal System (UPS) based on the cycle name and facility.

    Args:
        cycle_name (str): The name of the cycle to retrieve. e.g. "2024-1"
        facility (UpsFacilityName, optional): The facility for which to retrieve the cycle. Defaults to UpsFacilityName.nsls2.

    Returns:
        Optional[UpsCycle]: The retrieved cycle, or None if no cycle is found.

    Raises:
        UniversalProposalSystemException: If there is an error retrieving the cycle from UPS.

    """
    ups_facility_id = await facility_service.ups_id_for_facility(facility_name=facility)
    if not ups_facility_id:
        error_message: str = (
            f"Facility {facility} does not have a Universal Proposal System ID."
        )
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message)

    servicenow_table_name = "sn_customerservice_run_cycle"
    query=f"u_facility={ups_facility_id}^u_title={cycle_name}"
    url = f"{base_url}/now/table/{servicenow_table_name}?sysparm_query={query}&sysparm_display_value=all"

    logger.info(f"Getting cycles from UPS for {facility} facility.")

    cycle = None

    try:
        ups_cycle_response = await _call_ups_servicenow_webservice(url)
        ups_cycle = ups_cycle_response["result"]

        if len(ups_cycle) > 1:
            error_message = f"UPS returned more than one cycle for the {facility} facility with the name {cycle_name}."
            raise UniversalProposalSystemException(error_message)

        if ups_cycle and len(ups_cycle) > 0:
            cycle = UpsCycle(**ups_cycle[0])

    except ValidationError as error:
        error_message = f"Error validating cycle data recevied from UPS for the {facility} facility."
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message) from error
    except Exception as error:
        error_message = "Error retrieving cycle information from UPS."
        logger.exception(error_message)
        raise UniversalProposalSystemException(error_message) from error

    return cycle


async def get_cycles(
    facility: UpsFacilityName = UpsFacilityName.nsls2,
) -> list[UpsCycle]:
    ups_facility_id = await facility_service.ups_id_for_facility(facility_name=facility)
    if not ups_facility_id:
        error_message: str = (
            f"Facility {facility} does not have a Universal Proposal System ID."
        )
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message)

    cycles = []
    servicenow_table_name = "sn_customerservice_run_cycle"
    query = f"u_facility={ups_facility_id}"
    url = f"{base_url}/now/table/{servicenow_table_name}?sysparm_query={query}&sysparm_display_value=all"

    logger.info(f"Getting cycles from UPS for {facility} facility.")

    try:
        ups_cycle_list_response = await _call_ups_servicenow_webservice(url)
        ups_cycle_list = ups_cycle_list_response["result"]
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

async def get_mapping_of_cycles_for_proposal(proposal_ups_id: str) -> list[UpsRunCycleProposalMapping]:
    servicenow_table_name = "sn_customerservice_m2m_run_cycles_proposals"
    url = f"{base_url}/now/table/{servicenow_table_name}?sysparm_query=u_proposal={proposal_ups_id}&sysparm_display_value=all"

    results_list = []

    try:
        ups_response = await _call_ups_servicenow_webservice(url)
        mapping_list = ups_response["result"]
        if mapping_list and len(mapping_list) > 0:
            for mapping in mapping_list:
                results_list.append(UpsRunCycleProposalMapping(**mapping))
    except ValidationError as error:
        error_message = f"Error validating cycle to proposal mapping data recevied from UPS for proposal sysid {proposal_ups_id}."
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message) from error
    except Exception as error:
        error_message = "Error retrieving cycle to proposal mapping information from UPS."
        logger.exception(error_message)
        raise UniversalProposalSystemException(error_message) from error       
         
    return results_list

async def get_mapping_of_proposals_for_cycle(cycle_ups_id: str) -> list[UpsRunCycleProposalMapping]:
    servicenow_table_name = "sn_customerservice_m2m_run_cycles_proposals"
    url = f"{base_url}/now/table/{servicenow_table_name}?sysparm_query=u_run_cycle={cycle_ups_id}&sysparm_display_value=all"

    results_list = []

    try:
        ups_response = await _call_ups_servicenow_webservice(url)
        mapping_list = ups_response["result"]
        if mapping_list and len(mapping_list) > 0:    
            for mapping in mapping_list:
                results_list.append(UpsRunCycleProposalMapping(**mapping))
    except ValidationError as error:
        error_message = f"Error validating cycle to proposal mapping data recevied from UPS for proposal sysid {proposal_ups_id}."
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message) from error
    except Exception as error:
        error_message = "Error retrieving cycle to proposal mapping information from UPS."
        logger.exception(error_message)
        raise UniversalProposalSystemException(error_message) from error       
         
    return results_list


async def get_proposals_for_cycle(cycle_name: str, facility: UpsFacilityName = UpsFacilityName):
    cycle : UpsCycle= await get_cycle_by_name(cycle_name=cycle_name, facility=facility)
    if not cycle:
        error_message = f"No cycle found for {cycle_name} in the {facility} facility."
        logger.error(error_message)
        raise UniversalProposalSystemException(error_message)

    proposal_list = []
    mapping_list : list[UpsRunCycleProposalMapping] = await get_mapping_of_proposals_for_cycle(cycle.sys_id.value)
    if mapping_list and len(mapping_list) > 0:
        for mapping in mapping_list:
            proposal_list.append(mapping.u_proposal.display_value)

    return proposal_list


# async def get_institution_info(institution_id: str):
#     servicenow_table_name = "u_ror_data"


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


async def get_beamline(beamline_ups_id: str):
    servicenow_table_name = "sn_customerservice_beamlines"
    return