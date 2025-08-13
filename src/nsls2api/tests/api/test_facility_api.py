import pytest
from httpx import ASGITransport, AsyncClient
from datetime import datetime, timezone, timedelta
from nsls2api.models.cycles import Cycle

from nsls2api.api.models.facility_model import (
    FacilityCurrentOperatingCycleResponseModel,
    FacilityCyclesResponseModel,
    FacilityCycleResponseModel,
)
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
    assert current_cycle.cycle == "test-earlier"


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
    assert len(facility_cycles.cycles) == 3
    assert facility_cycles.cycles[0] == "1999-1"


@pytest.mark.asyncio
async def test_get_proposals_for_cycle():
    facility_name = "nsls2"
    cycle_name = "1999-1"

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/v1/facility/{facility_name}/cycle/{cycle_name}/proposals"
        )

    response_json = response.json()
    assert response.status_code == 200

    # This should be returning a CycleProposalList
    cycle_proposals = CycleProposalList(**response_json)
    assert cycle_proposals.cycle == cycle_name

    # For now we are not returning any proposals
    assert len(cycle_proposals.proposals) == 0
    assert cycle_proposals.count == 0

@pytest.mark.anyio
async def test_get_cycle_by_earlier_date_and_today_and_update_admin(db):
    facility_name = "nsls2"
    today = datetime.now(timezone.utc).date()
    earlier_date = today - timedelta(days=25)

    # 1. Get cycle by earlier date (should be current)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp_earlier = await ac.get(
            f"/v1/facility/{facility_name}/cycle_by_date?date={earlier_date.isoformat()}"
        )
    assert resp_earlier.status_code == 200
    cycle_earlier = FacilityCycleResponseModel(**resp_earlier.json())
    assert cycle_earlier.cycle == "test-earlier"
    assert cycle_earlier.is_current_operating_cycle is True
   
    # 2. Get cycle by today's date (should NOT be current)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp_today = await ac.get(
            f"/v1/facility/{facility_name}/cycle_by_date?date={today.isoformat()}"
        )
    assert resp_today.status_code == 200
    cycle_today = FacilityCycleResponseModel(**resp_today.json())
    assert cycle_today.cycle == "test-current"
    assert cycle_today.is_current_operating_cycle is False

    # 3. Call admin endpoint to set current cycle by today
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp_admin = await ac.post(
            f"/v1/facility/{facility_name}/cycles/set_current_cycle_by_today", json={}
        )

    cycle_admin = FacilityCycleResponseModel(**resp_admin.json())
    assert resp_admin.status_code == 200
    assert cycle_admin.cycle == "test-current"
    assert cycle_admin.is_current_operating_cycle is True

    # 4. Check DB: only test-current is now current, test-earlier is not
    current = await Cycle.find_one(Cycle.name == "test-current", Cycle.facility == facility_name)
    earlier = await Cycle.find_one(Cycle.name == "test-earlier", Cycle.facility == facility_name)

    assert current.is_current_operating_cycle is True
    assert earlier.is_current_operating_cycle is False

    # 5. Optionally, re-query API to confirm state
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp_earlier2 = await ac.get(
            f"/v1/facility/{facility_name}/cycle_by_date?date={earlier_date.isoformat()}"
        )
        resp_today2 = await ac.get(
            f"/v1/facility/{facility_name}/cycle_by_date?date={today.isoformat()}"
        )
    cycle_earlier2 = FacilityCycleResponseModel(**resp_earlier2.json())
    cycle_today2 = FacilityCycleResponseModel(**resp_today2.json())
    print("Cycle by earlier date:", cycle_earlier2)
    print("Cycle by today date:", cycle_today2)
    assert cycle_earlier2.is_current_operating_cycle is False
    assert cycle_today2.is_current_operating_cycle is True


@pytest.mark.anyio
async def test_set_current_cycle_by_specific_date_admin():
    facility_name = "nsls2"
    test_date = "1999-02-01"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/v1/facility/{facility_name}/cycle_by_date?date={test_date}"
        )

    print("API response:", response.status_code, response.json())

    assert response.status_code in (200, 404)
    if response.status_code == 200:
        response_json = response.json()
        cycle = FacilityCycleResponseModel(**response_json)
        assert cycle.facility == facility_name
        start = datetime.fromisoformat(cycle.start_date).date()
        end = datetime.fromisoformat(cycle.end_date).date()
        assert start <= datetime.fromisoformat(test_date).date() <= end

@pytest.mark.anyio
async def test_set_current_cycle_by_today_admin_different_facility():
    facility_name = "lbms"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(f"/v1/facility/{facility_name}/cycles/set_current_cycle_by_today")
    print("API response:", response.status_code, response.json())
    # Should be 404 unless you have a cycle for today for this facility
    assert response.status_code == 404
    assert "error" in response.json() or "detail" in response.json()