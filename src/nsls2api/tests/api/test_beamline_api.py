import pytest
from httpx import AsyncClient
from nsls2api.models.beamlines import ServiceAccounts, Beamline
from nsls2api.models.validation_error import ValidationError


async def test_get_beamline_service_accounts(test_client: AsyncClient):
    response = await test_client.get("/v1/beamline/tst/service-accounts")
    response_json = response.json()
    assert response.status_code == 200

    # Make sure we can create a ServiceAccounts object from the response
    accounts = ServiceAccounts(**response_json)
    assert accounts.workflow == "workflow-tst"
    assert accounts.ioc == "softioc-tst"
    assert accounts.bluesky == "bluesky-tst"
    assert accounts.epics_services == "epics-services-tst"
    assert accounts.operator == "xf31id"
    assert accounts.lsdc is None or accounts.lsdc == ""


async def test_get_beamline_lowercase(test_client: AsyncClient):
    response = await test_client.get("/v1/beamline/tst")
    response_json = response.json()
    assert response.status_code == 200

    # Make sure we can create a Beamline object from the response
    beamline = Beamline(**response_json)
    assert beamline.name == "TST"

async def test_get_beamline_uppercase(test_client: AsyncClient):
    response = await test_client.get("/v1/beamline/TST")
    response_json = response.json()
    assert response.status_code == 200

    # Make sure we can create a Beamline object from the response
    beamline = Beamline(**response_json)
    assert beamline.name == "TST"

async def test_get_beamline_directory_skeleton(test_client: AsyncClient):
    response = await test_client.get("/v1/beamline/tst/directory-skeleton")
    response_json = response.json()
    assert response.status_code == 200
