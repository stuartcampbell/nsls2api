import pytest
from httpx import ASGITransport, AsyncClient

from nsls2api.main import app
from nsls2api.api.models.proposal_model import (
    ProposalChangeResultsList,
    LockedProposalsList,
    ProposalFullDetailsList
)
from nsls2api.services import (
    proposal_service
)
from nsls2api.models.apikeys import ApiKey
import os

test_proposal_id = "314159"

test_beamline_name = "ZZZ"

test_cycle_name = "1999-1"

facility = "nsls2"



# @pytest.mark.anyio
# async def test_get_proposal():
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as ac:
#         response = await ac.get( f"/v1/proposals/?proposal_id={test_proposal_id}")
#     response_json = response.json()
#     assert response.status_code == 200
#     proposal_info = ProposalFullDetailsList(**response_json)
#     assert proposal_info.proposals[0].proposal_id == test_proposal_id


@pytest.mark.anyio
async def test_lock_and_unlock_proposals():
    #resetting to ensure locked is false
    key = await ApiKey.find_one(ApiKey.username == "test_user")
    data_start = {"proposals_to_change": [test_proposal_id]}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response_start = await ac.put( f"/v1/proposals/unlock",
                json=data_start,headers={"Authorization": key.secret_key})
        
    response_start_json = response_start.json()
    assert response_start.status_code == 200
    unlocked_proposals_info = ProposalChangeResultsList(**response_start_json)
    assert unlocked_proposals_info.successful_proposals == [test_proposal_id]
    proposal_objects_start = await proposal_service.fetch_proposals(proposal_id = [test_proposal_id])
    assert proposal_objects_start[0].locked == False

    #locking
    data_lock = {"proposals_to_change": [test_proposal_id]}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response_lock = await ac.put( f"/v1/proposals/lock",
                json=data_lock,headers={"Authorization": key.secret_key})
        
    response_lock_json = response_lock.json()
    assert response_lock.status_code == 200
    locked_proposals_info = ProposalChangeResultsList(**response_lock_json)
    assert locked_proposals_info.successful_proposals == [test_proposal_id]
    proposal_objects = await proposal_service.fetch_proposals(proposal_id = [test_proposal_id])
    assert proposal_objects[0].locked == True

    #gathering locked proposals
    # facility_name = "nsls2",
    # beamline = "ZZZ"
    # async with AsyncClient(
    #     transport=ASGITransport(app=app), base_url="http://test"
    # ) as ac:
    #     response_get_list = await ac.get(
    #         f"/v1/proposals/locked?beamline={beamline}?facility={facility_name}",headers={"Authorization": key.secret_key}
    #     )
    # response_get_list_json = response_get_list.json()
    # assert response_get_list.status_code == 200
    # locked_proposals_list = LockedProposalsList(**response_get_list_json)
    # assert locked_proposals_list.locked_proposals == [test_proposal_id] 


    #unlocking
    data_unlock = {"proposals_to_change": [test_proposal_id]}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response_unlock = await ac.put( f"/v1/proposals/unlock",
                json=data_unlock,headers={"Authorization": key}) 
        
    response_unlock_json = response_unlock.json()
    assert response_unlock.status_code == 200
    unlocked_proposals_info = ProposalChangeResultsList(**response_unlock_json)
    assert unlocked_proposals_info.successful_proposals == [test_proposal_id]
    proposal_objects = await proposal_service.fetch_proposals(proposal_id = [test_proposal_id])
    assert proposal_objects[0].locked == False

@pytest.mark.anyio
async def test_lock_and_unlock_beamlines():
    key = await ApiKey.find_one(ApiKey.username == "test_user")
    # start with unlocking to ensure its unlocked
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response_start = await ac.put( f"/v1/proposals/beamline/unlock/{test_beamline_name}",headers={"Authorization": key.secret_key})
    
    response_start_json = response_start.json()
    assert response_start.status_code == 200
    start_beamline_info = ProposalChangeResultsList(**response_start_json)
    assert start_beamline_info.successful_proposals == [test_proposal_id]
    proposal_objects = await proposal_service.fetch_proposals(proposal_id = [test_proposal_id])
    assert proposal_objects[0].locked == False


    # lock beamline
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response_lock = await ac.put( f"/v1/proposals/beamline/lock/{test_beamline_name}",headers={"Authorization": key.secret_key})
    
    response_lock_json = response_lock.json()
    assert response_lock.status_code == 200
    locked_beamline_info = ProposalChangeResultsList(**response_lock_json)
    assert locked_beamline_info.successful_proposals == [test_proposal_id]
    proposal_objects = await proposal_service.fetch_proposals(proposal_id = [test_proposal_id])
    assert proposal_objects[0].locked == True

    #unlock beamline 
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response_unlock = await ac.put( f"/v1/proposals/beamline/unlock/{test_beamline_name}",headers={"Authorization": key.secret_key})
    
    response_unlock_json = response_unlock.json()
    assert response_unlock.status_code == 200
    unlocked_beamline_info = ProposalChangeResultsList(**response_unlock_json)
    assert unlocked_beamline_info.successful_proposals == [test_proposal_id]
    proposal_objects = await proposal_service.fetch_proposals(proposal_id = [test_proposal_id])
    assert proposal_objects[0].locked == False


@pytest.mark.anyio
async def test_lock_and_unlock_cycles():
    key = await ApiKey.find_one(ApiKey.username == "test_user")
    # start with unlocking to ensure its unlocked
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response_start = await ac.put( f"/v1/proposals/cycle/unlock/{test_cycle_name}/{facility}",headers={"Authorization": key.secret_key})
    
    response_start_json = response_start.json()
    assert response_start.status_code == 200
    start_info = ProposalChangeResultsList(**response_start_json)
    assert start_info.successful_proposals == [test_proposal_id]
    proposal_objects = await proposal_service.fetch_proposals(proposal_id = [test_proposal_id])
    assert proposal_objects[0].locked == False


    # lock beamline
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response_lock = await ac.put( f"/v1/proposals/cycle/lock/{test_cycle_name}/{facility}",headers={"Authorization": key.secret_key})
    
    response_lock_json = response_lock.json()
    assert response_lock.status_code == 200
    locked_cycle_info = ProposalChangeResultsList(**response_lock_json)
    assert locked_cycle_info.successful_proposals == [test_proposal_id]
    proposal_objects = await proposal_service.fetch_proposals(proposal_id = [test_proposal_id])
    assert proposal_objects[0].locked == True

    #unlock beamline 
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response_unlock = await ac.put( f"/v1/proposals/cycle/unlock/{test_cycle_name}/{facility}",headers={"Authorization": key.secret_key})
    
    response_unlock_json = response_unlock.json()
    assert response_unlock.status_code == 200
    unlocked_cycle_info = ProposalChangeResultsList(**response_unlock_json)
    assert unlocked_cycle_info.successful_proposals == [test_proposal_id]
    proposal_objects = await proposal_service.fetch_proposals(proposal_id = [test_proposal_id])
    assert proposal_objects[0].locked == False



