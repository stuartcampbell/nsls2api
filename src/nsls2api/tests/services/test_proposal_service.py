import datetime
import pytest
from nsls2api.models.proposals import Proposal
from nsls2api.services.proposal_service import is_test_proposal

@pytest.mark.asyncio
async def test_is_test_proposal():
    # Create a test proposal
    proposal = Proposal(
        proposal_id="123456",
        title="Test Proposal",
        type="Fake Test Proposal",
        users=[],
        pass_type_id="666666",
        data_session="pass-123456",
        instruments=["TST"],
        cycles=["2022-1"],
        last_updated=datetime.datetime.now(),
    )

    # Test if the proposal is a test proposal
    assert await is_test_proposal(proposal) is True

    # Create a non-test proposal
    proposal = Proposal(
        proposal_id="789012",
        title="Regular Proposal",
        type="Regular Proposal",
        users=[],
        pass_type_id="123456",
        data_session="pass-789012",
        instruments=["TST"],
        cycles=["2022-1"],
        last_updated=datetime.datetime.now(),
    )

    # Test if the proposal is a test proposal
    assert await is_test_proposal(proposal) is False