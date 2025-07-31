import pytest

from nsls2api.models.proposals import Proposal
from nsls2api.services import proposal_service

test_proposal_id = "314159"

test_beamline_name = "ZZZ"

test_beamline_name_lower = "zzz"


@pytest.mark.anyio
async def test_get_beamline_specific_slack_channel_for_proposal():
    slack_channels = (
        await proposal_service.get_beamline_specific_slack_channel_for_proposal(
            proposal_id=test_proposal_id
        )
    )
    # For a single beamline proposal we should only have 1 channel
    assert len(slack_channels) == 1
    assert slack_channels[0] == f"pass-{test_proposal_id}-zzz"


@pytest.mark.anyio
async def test_proposal_by_id():
    proposal: Proposal = await proposal_service.proposal_by_id(test_proposal_id)
    assert proposal is not None
    assert proposal.proposal_id == test_proposal_id


@pytest.mark.anyio
async def test_proposal_type_description_from_pass_type_id():
    test_proposal_type_id = 999999
    description = await proposal_service.proposal_type_description_from_pass_type_id(
        test_proposal_type_id
    )
    assert description is not None
    assert description == "Proposal Type X"


@pytest.mark.anyio
async def test_proposal_type_description_from_nonexistent_pass_type_id():
    test_proposal_type_id = 999991  # non-existent proposal type_id
    try:
        await proposal_service.proposal_type_description_from_pass_type_id(
            test_proposal_type_id
        )
        # If we get past the above line without an exception then something's wrong
        assert False
    except LookupError:
        # If we threw a LookupError for the non-existent type_id
        # then all is good.
        assert True


@pytest.mark.anyio
async def test_data_session_for_proposal():
    data_session = await proposal_service.data_session_for_proposal(
        proposal_id=test_proposal_id
    )
    assert data_session is not None
    assert data_session == f"pass-{test_proposal_id}"


@pytest.mark.anyio
async def test_beamlines_for_proposal():
    beamlines = await proposal_service.beamlines_for_proposal(
        proposal_id=test_proposal_id
    )
    assert beamlines is not None
    assert len(beamlines) == 1
    assert beamlines[0] == "ZZZ"


@pytest.mark.anyio
async def test_cycles_for_proposal():
    cycles = await proposal_service.cycles_for_proposal(proposal_id=test_proposal_id)
    assert cycles is not None
    assert len(cycles) == 1
    assert cycles[0] == "1999-1"


@pytest.mark.anyio
async def test_is_commissioning():
    proposal = await proposal_service.proposal_by_id(test_proposal_id)
    assert await proposal_service.is_commissioning(proposal) is False


@pytest.mark.anyio
async def test_case_sensitivity_fetch_proposals():
    proposal_objects_upper = await proposal_service.fetch_proposals(
        beamline=[test_beamline_name]
    )
    proposal_objects_lower = await proposal_service.fetch_proposals(
        beamline=[test_beamline_name_lower]
    )

    assert proposal_objects_upper == proposal_objects_lower
    assert proposal_objects_lower[0].proposal_id == test_proposal_id