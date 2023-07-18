from typing import Optional

from nsls2api.models.proposals import Proposal


async def proposal_count() -> int:
    return await Proposal.count()


async def proposal_by_id(proposal_id: str) -> Optional[Proposal]:
    """
    Retrieve a proposal by its ID.

    :param proposal_id: The ID of the proposal to retrieve.
    :return: The proposal if found, or None if not found.
    """
    proposal = await Proposal.find_one(Proposal.proposal_id == proposal_id)
    return proposal
