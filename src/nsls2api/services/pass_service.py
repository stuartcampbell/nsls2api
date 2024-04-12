from typing import Optional

from pydantic import ValidationError

from nsls2api.api.models.facility_model import FacilityName
from nsls2api.infrastructure import config
from nsls2api.infrastructure.logging import logger
from nsls2api.models.pass_models import (
    PassCycle,
    PassProposal,
    PassProposalType,
    PassSaf,
)
from nsls2api.services import facility_service
from nsls2api.services.helpers import _call_async_webservice

settings = config.get_settings()

api_key = settings.pass_api_key
base_url = settings.pass_api_url


class PassException(Exception):
    pass


async def get_proposal(
    proposal_id: int, facility: FacilityName = FacilityName.nsls2
) -> Optional[PassProposal]:
    pass_facility = await facility_service.pass_id_for_facility(facility)

    if not pass_facility:
        error_message: str = f"Facility {facility} does not have a PASS ID."
        logger.error(error_message)
        raise PassException(error_message)

    url = f"{base_url}/Proposal/GetProposal/{api_key}/{pass_facility}/{proposal_id}"

    try:
        pass_proposal = await _call_async_webservice(url)
        proposal = PassProposal(**pass_proposal)
    except ValidationError as error:
        error_message = (
            f"Error validating data recevied from PASS for proposal {proposal_id}."
        )
        logger.error(error_message)
        raise PassException(error_message) from error
    except Exception as error:
        error_message = f"Error retrieving proposal {proposal_id} from PASS."
        logger.exception(error_message)
        raise PassException(error_message) from error

    return proposal


async def get_proposal_types(facility) -> Optional[PassProposalType]:
    pass_facility = await facility_service.pass_id_for_facility(facility)

    if not pass_facility:
        error_message: str = f"Facility {facility} does not have a PASS ID."
        logger.error(error_message)
        raise PassException(error_message)

    url = f"{base_url}/Proposal/GetProposalTypes/{api_key}/{pass_facility}"

    try:
        pass_proposal_types_list = await _call_async_webservice(url)
        proposal_types = []
        if pass_proposal_types_list and len(pass_proposal_types_list) > 0:
            for proposal_type in pass_proposal_types_list:
                proposal_types.append(PassProposalType(**proposal_type))
    except ValidationError as error:
        error_message = f"Error validating data recevied from PASS for proposal type for the {facility} facility."
        logger.error(error_message)
        raise PassException(error_message) from error
    except Exception as error:
        error_message = "Error retrieving proposal types from PASS."
        logger.error(error_message)
        raise PassException(error_message) from error

    return proposal_types


async def get_saf_from_proposal(
    proposal_id: int, facility: FacilityName = FacilityName.nsls2
):
    pass_facility = await facility_service.pass_id_for_facility(facility)

    if not pass_facility:
        error_message: str = f"Facility {facility} does not have a PASS ID."
        logger.error(error_message)
        raise PassException(error_message)

    url = f"{base_url}/SAF/GetSAFsByProposal/{api_key}/{pass_facility}/{proposal_id}"
    try:
        pass_saf_list = await _call_async_webservice(url)
        saf_list = []
        if pass_saf_list and len(pass_saf_list) > 0:
            for saf in pass_saf_list:
                saf_list.append(PassSaf(**saf))
    except ValidationError as error:
        error_message = (
            f"Error validating SAF data recevied from PASS for proposal {proposal_id}."
        )
        logger.error(error_message)
        raise PassException(error_message) from error
    except Exception as error:
        error_message = f"Error retrieving SAFs for proposal {proposal_id} from PASS."
        logger.exception(error_message)
        raise PassException(error_message) from error

    return saf_list


async def get_commissioning_proposals_by_year(year: int):
    # The PASS ID for commissioning proposals is 300005
    url = f"{base_url}Proposal/GetProposalsByType/{api_key}/NSLS-II/{year}/300005/NULL"
    proposals = await _call_async_webservice(url)
    return proposals


async def get_pass_resources():
    url = f"{base_url}/Resource/GetResources/{api_key}/NSLS-II"
    resources = await _call_async_webservice(url)
    return resources


async def get_cycles() -> PassCycle:
    url = f"{base_url}/Proposal/GetCycles/{api_key}/NSLS-II"
    print(url)
    cycles = await _call_async_webservice(url)
    return PassCycle(**cycles)


async def get_proposals_allocated():
    url = f"{base_url}/Proposal/GetProposalsAllocated/{api_key}/NSLS-II"
    allocated_proposals = await _call_async_webservice(url)
    return allocated_proposals


async def get_proposals_by_person(bnl_id: str):
    url = f"{base_url}/Proposal/GetProposalsByPerson/{api_key}/NSLS-II/null/null/{bnl_id}/null"
    print(url)
    proposals = await _call_async_webservice(url)
    return proposals
