from typing import Optional

# from models.proposals import Proposal
from nsls2api.models.proposals import Proposal


async def proposal_count() -> int:
    return await Proposal.count()


async def recently_updated(count=5):
    """
    Function to fetch recently updated proposals.

    :param count: Specifies the number of recently updated proposals to fetch. Defaults to 5.
    :type count: int

    :return: List of recently updated proposals.
    :rtype: list[Proposal]
    """
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

# async def users_from_proposal(proposal_id: str) -> Optional[Proposal]:
#
#     proposal = await proposal_by_id(proposal_id)
#     if proposal is None:
#         raise Exception(f"No proposal with ID {proposal_id} found.")
#
#     user_list = await Proposal.find_one(Proposal.proposal_id == proposal_id).project()
#     return user_list
