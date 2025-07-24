import pytest

from nsls2api.services import facility_service

valid_cycle_name = "1999-1"


@pytest.mark.anyio
async def test_get_pass_id_for_facility():
    pass_id = await facility_service.pass_id_for_facility("nsls2")
    assert pass_id == "NSLS-II"


@pytest.mark.anyio
async def test_get_facility_by_pass_id():
    facility = await facility_service.facility_by_pass_id("NSLS-II")
    assert facility.name == "NSLS-II"
    assert facility.facility_id == "nsls2"


@pytest.mark.anyio
async def test_get_data_admin_group():
    data_admin_group = await facility_service.data_admin_group("nsls2")
    assert data_admin_group == "nsls2-data-admins"


@pytest.mark.anyio
async def test_get_data_admins():
    data_admins = await facility_service.get_data_admins("nsls2")
    assert data_admins == ["testy-mcdata"]


@pytest.mark.anyio
async def test_facilities_count():
    assert await facility_service.facilities_count() == 1


@pytest.mark.anyio
async def test_all_facilities():
    facilities = await facility_service.all_facilities()
    assert type(facilities) is list


@pytest.mark.anyio
async def test_get_current_operating_cycle():
    cycle = await facility_service.current_operating_cycle("nsls2")
    assert cycle == valid_cycle_name


@pytest.mark.anyio
async def test_set_current_operating_cycle():
    cycle = await facility_service.set_current_operating_cycle(
        "nsls2", valid_cycle_name
    )
    assert cycle == valid_cycle_name


@pytest.mark.anyio
async def test_set_current_operating_cycle_invalid():
    with pytest.raises(facility_service.CycleNotFoundError):
        await facility_service.set_current_operating_cycle("nsls2", "invalid-cycle")


@pytest.mark.anyio
async def test_cycle_year():
    cycle = await facility_service.cycle_year(valid_cycle_name)
    assert cycle == "1999"


@pytest.mark.anyio
async def test_cycle_exists():
    cycle_exists = await facility_service.cycle_exists(
        cycle_name=valid_cycle_name, facility="nsls2"
    )
    assert cycle_exists == True

    invalid_cycle_exists = await facility_service.cycle_exists(
        cycle_name="invalid_cycle", facility="nsls2"
    )
    assert invalid_cycle_exists == False
