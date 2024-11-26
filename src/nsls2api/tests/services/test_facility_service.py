import pytest

from nsls2api.services import facility_service


@pytest.mark.anyio
async def test_facilities_count():
    assert await facility_service.facilities_count() == 1


@pytest.mark.anyio
async def test_all_facilities():
    facilities = await facility_service.all_facilities()
    assert type(facilities) is list
