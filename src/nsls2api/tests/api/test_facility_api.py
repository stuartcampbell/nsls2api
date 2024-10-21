import pytest
from httpx import AsyncClient, ASGITransport

from nsls2api.api.models.facility_model import FacilityCyclesResponseModel, FacilityCurrentOperatingCycleResponseModel
from nsls2api.api.models.proposal_model import CycleProposalList
from nsls2api.main import app


@pytest.mark.anyio
async def test_get_current_operating_cycle():
    facility_name = "nsls2"
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"/v1/facility/{facility_name}/cycles/current")

    response_json = response.json()
    assert response.status_code == 200

    # This should be returning a FacilityCurrentOperatingCycleResponseModel
    current_cycle = FacilityCurrentOperatingCycleResponseModel(**response_json)
    assert current_cycle.facility == facility_name
    assert current_cycle.cycle == "1999-1"


@pytest.mark.anyio
async def test_get_facility_cycles():
    facility_name = "nsls2"
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"/v1/facility/{facility_name}/cycles")

    response_json = response.json()
    assert response.status_code == 200

    # This should be returning a FacilityCyclesResponseModel
    facility_cycles = FacilityCyclesResponseModel(**response_json)
    assert facility_cycles.facility == facility_name
    assert len(facility_cycles.cycles) == 1
    assert facility_cycles.cycles[0] == "1999-1"


@pytest.mark.asyncio
async def test_get_proposals_for_cycle():
    facility_name = "nsls2"
    cycle_name = "1999-1"

    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"/v1/facility/{facility_name}/cycle/{cycle_name}/proposals")

    response_json = response.json()
    assert response.status_code == 200

    # This should be returning a CycleProposalList
    cycle_proposals = CycleProposalList(**response_json)
    assert cycle_proposals.cycle == cycle_name

    # For now we are not returning any proposals
    assert len(cycle_proposals.proposals) == 0
    assert cycle_proposals.count == 0
