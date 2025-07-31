import pytest

from nsls2api.services import proposal_service

test_beamline_name = "ZZZ"

test_beamline_name_lower = "zzz"

test_proposal_id = "314159"

@pytest.mark.anyio
async def test_case_sensitivity_fetch_proposals():
    proposal_objects_upper = await proposal_service.fetch_proposals(
        beamline=[test_beamline_name]
    )
    proposal_objects_lower = await proposal_service.fetch_proposals(
        beamline=[test_beamline_name_lower]
    )

    assert proposal_objects_upper == proposal_objects_lower
    assert proposal_objects_lower.proposal_id[0] == test_proposal_id