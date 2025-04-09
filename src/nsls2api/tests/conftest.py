import datetime

import pytest_asyncio

from nsls2api import models
from nsls2api.infrastructure.config import get_settings
from nsls2api.infrastructure.mongodb_setup import init_connection
from nsls2api.models.beamlines import Beamline, ServiceAccounts
from nsls2api.models.cycles import Cycle
from nsls2api.models.facilities import Facility
from nsls2api.models.proposal_types import ProposalType
from nsls2api.models.proposals import Proposal


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def db():
    settings = get_settings()
    await init_connection(settings.mongodb_dsn)

    # Insert a beamline into the database
    beamline = Beamline(
        name="ZZZ",
        port="66-ID-6",
        long_name="Magical PyTest X-Ray Beamline",
        alternative_name="66-ID",
        network_locations=["xf66id6"],
        pass_name="Beamline 66-ID-6",
        pass_id="666666",
        nsls2_redhat_satellite_location_name="Nowhere",
        service_accounts=ServiceAccounts(
            ioc="testy-mctestface-ioc",
            bluesky="testy-mctestface-bluesky",
            epics_services="testy-mctestface-epics-services",
            operator="testy-mctestface-xf66id6",
            workflow="testy-mctestface-workflow",
        ),
    )
    await beamline.insert()

    # Insert a facility into the database
    facility = Facility(
        name="NSLS-II",
        facility_id="nsls2",
        fullname="National Synchrotron Light Source II",
        pass_facility_id="NSLS-II",
    )
    await facility.insert()

    # Insert a cycle into the database
    cycle = Cycle(
        name="1999-1",
        facility="nsls2",
        year="1999",
        start_date=datetime.datetime.fromisoformat("1999-01-01"),
        end_date=datetime.datetime.fromisoformat("1999-06-30"),
        is_current_operating_cycle=True,
        pass_description="January - June",
        pass_id="111111",
    )
    await cycle.insert()

    # Insert a proposal type into the database
    proposal_type = ProposalType(
        code="X",
        facility_id="nsls2",
        description="Proposal Type X",
        pass_id="999999",
        pass_description="Proposal Type X",
    )
    await proposal_type.insert()

    # Insert a proposal into the database
    test_proposal_id = "314159"
    proposal = Proposal(
        proposal_id=test_proposal_id,
        data_session=f"pass-{test_proposal_id}",
        title="Test Proposal",
        type=proposal_type.description,
        pass_type_id=proposal_type.pass_id,
        instruments=["ZZZ"],
        cycles=[cycle.name],
        users=[],
        safs=[],
        slack_channels=[],
        created_on=datetime.datetime.fromisoformat("1999-01-01"),
        last_updated=datetime.datetime.now(),
    )
    await proposal.insert()

    yield

    # Cleanup the database collections
    for model in models.all_models:
        print(f"dropping {model}")
        await model.get_motor_collection().drop()
        await model.get_motor_collection().drop_indexes()
