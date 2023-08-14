from typing import Optional

from beanie.operators import In

# from models.proposals import Proposal
from nsls2api.models.proposals import Proposal, User


async def exists(proposal_id: str) -> bool:
    proposal = await Proposal.find_one(Proposal.proposal_id == proposal_id)
    return False if proposal is None else True


async def proposal_count() -> int:
    return await Proposal.count()


async def recently_updated(count=5, beamline=None):
    """
    Function to fetch recently updated proposals.

    :param count: Specifies the number of recently updated proposals to fetch. Defaults to 5.
    :type count: int

    :return: List of recently updated proposals.
    :rtype: list[Proposal]

    Args:
        beamline: Optional beamline to restrict list of proposals to
    """
    if beamline:
        print(f"Searching for proposals within {beamline}...")
        query = In(Proposal.instruments, [beamline])
        updated = await Proposal.find_many(query).sort(-Proposal.last_updated).limit(count).to_list()
    else:
        updated = await Proposal.find_all().sort(-Proposal.last_updated).limit(count).to_list()
    return updated


async def proposal_by_id(proposal_id: str) -> Optional[Proposal]:
    """
    Retrieve a proposal by its ID.

    :param proposal_id: The ID of the proposal to retrieve.
    :return: The proposal if found, or None if not found.
    """

    if not proposal_id:
        return None
    proposal_id = proposal_id.lower().strip()

    proposal: Proposal = await Proposal.find_one(Proposal.proposal_id == proposal_id)
    return proposal


async def users_from_proposal(proposal_id: str) -> Optional[list[User]]:
    proposal = await proposal_by_id(proposal_id)
    return proposal.users


async def usernames_from_proposal(proposal_id: str) -> Optional[list[str]]:
    proposal = await proposal_by_id(proposal_id)

    if proposal is None:
        raise Exception(f'Proposal {proposal_id} not found')

    usernames = [
        u.username
        for u in proposal.users if u.username is not None
    ]
    return usernames


async def pi_from_proposal(proposal_id: str) -> Optional[list[User]]:
    proposal = await proposal_by_id(proposal_id)

    pi = [
        u for u in proposal.users if u.is_pi
    ]

    # TODO: Check for multiple of no PIs

    return pi
