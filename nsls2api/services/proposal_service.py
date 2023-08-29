from typing import Optional

from beanie.operators import In

# from models.proposals import Proposal
from nsls2api.models.proposals import Proposal, User, ProposalIdView


async def exists(proposal_id: int) -> bool:
    proposal = await Proposal.find_one(Proposal.proposal_id == str(proposal_id))
    return False if proposal is None else True


async def proposal_count() -> int:
    return await Proposal.count()


async def recently_updated(count=5, beamline: str | None = None):
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
        # Ensure we match the case in the database for the beamline name
        beamline = beamline.upper()
        # print(f"Searching for proposals within {beamline}...")
        query = In(Proposal.instruments, [beamline])
        updated = (
            await Proposal.find_many(query)
            .sort(-Proposal.last_updated)
            .limit(count)
            .to_list()
        )
    else:
        updated = (
            await Proposal.find_many()
            .sort(-Proposal.last_updated)
            .limit(count)
            .to_list()
        )
    return updated


async def proposal_by_id(proposal_id: int) -> Optional[Proposal]:
    """
    Retrieve a proposal by its ID.

    :param proposal_id: The ID of the proposal to retrieve.
    :return: The proposal if found, or None if not found.
    """

    if not proposal_id:
        return None

    # proposal_id = proposal_id.strip()
    proposal: Proposal = await Proposal.find_one(Proposal.proposal_id == str(proposal_id))

    print(proposal)

    return proposal


async def fetch_users_on_proposal(proposal_id: int) -> Optional[list[User]]:
    proposal = await proposal_by_id(proposal_id)
    return proposal.users


async def usernames_from_proposal(proposal_id: int) -> Optional[list[str]]:
    proposal = await proposal_by_id(proposal_id)

    if proposal is None:
        raise Exception(f"Proposal {proposal_id} not found")

    usernames = [u.username for u in proposal.users if u.username is not None]
    return usernames


async def pi_from_proposal(proposal_id: int) -> Optional[list[User]]:
    proposal = await proposal_by_id(proposal_id)

    pi = [u for u in proposal.users if u.is_pi]

    # TODO: Check for multiple or no PIs

    return pi


async def commissioning_proposals(beamline: str | None = None):

    if beamline:
        # Ensure we match the case in the database for the beamline name
        beamline = beamline.upper()

        proposals = (
            Proposal.find(Proposal.pass_type_id == "300005", projection_model=ProposalIdView)
        )

    else:
        query = In(Proposal.instruments, [beamline])
        proposals = (
            Proposal.find(Proposal.pass_type_id == "300005").find(query, projection_model=ProposalIdView)
        )

    commissioning_proposal_list = [p.proposal_id for p in await proposals.to_list() if p.proposal_id is not None]

    return commissioning_proposal_list
