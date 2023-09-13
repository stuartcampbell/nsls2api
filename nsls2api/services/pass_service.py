from typing import Optional

import httpx
from httpx import Response

from nsls2api.infrastructure import config
from .helpers import _call_async_webservice

settings = config.get_settings()

api_key = settings.pass_api_key
base_url = settings.pass_api_url

async def get_proposal(proposal_id: int):
    url = f'{base_url}/Proposal/GetProposal/{api_key}/NSLS-II/{proposal_id}'
    print(url)
    proposal = await _call_async_webservice(url)
    return proposal


async def get_saf_from_proposal(proposal_id: int):
    url = f'{base_url}/SAF/GetSAFsByProposal/{api_key}/NSLS-II/{proposal_id}'
    print(url)
    saf = await _call_async_webservice(url)
    return saf


async def get_commissioning_proposals_by_year(year: int):
    url = f"{base_url}Proposal/GetProposalsByType/{api_key}/NSLS-II/{year}/300005/NULL"
    proposals = await _call_async_webservice(url)
    return proposals


async def get_pass_resources():
    url = f'{base_url}/Resource/GetResources/{api_key}/NSLS-II'
    resources = await _call_async_webservice(url)
    return resources


async def get_cycles():
    url = f'{base_url}/Proposal/GetCycles/{api_key}/NSLS-II'
    print(url)
    cycles = await _call_async_webservice(url)
    return cycles


async def get_proposals_allocated():
    url = f'{base_url}/Proposal/GetProposalsAllocated/{api_key}/NSLS-II'
    allocated_proposals = await _call_async_webservice(url)
    return allocated_proposals


async def get_proposals_by_person(bnl_id: str):
    url = f'{base_url}/Proposal/GetProposalsByPerson/{api_key}/NSLS-II/null/null/{bnl_id}/null'
    print(url)
    proposals = await _call_async_webservice(url)
    return proposals
