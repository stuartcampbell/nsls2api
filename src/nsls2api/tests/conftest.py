import pytest_asyncio

from nsls2api import models
from nsls2api.infrastructure.config import get_settings
from nsls2api.infrastructure.mongodb_setup import init_connection
from nsls2api.models.beamlines import Beamline, ServiceAccounts
from nsls2api.models.cycles import Cycle
from nsls2api.models.facilities import Facility
from nsls2api.models.proposal_types import ProposalType


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def db():
    settings = get_settings()
    await init_connection(settings.mongodb_dsn)

    # Insert a beamline into the database
    beamline = Beamline(name="ZZZ", port="66-ID-6", long_name="Magical PyTest X-Ray Beamline",
                        alternative_name="66-ID", network_locations=["xf66id6"],
                        pass_name="Beamline 66-ID-6", pass_id="666666",
                        nsls2_redhat_satellite_location_name="Nowhere",
                        service_accounts=ServiceAccounts(ioc="testy-mctestface-ioc",
                                                         bluesky="testy-mctestface-bluesky",
                                                         epics_services="testy-mctestface-epics-services",
                                                         operator="testy-mctestface-xf66id6",
                                                         workflow="testy-mctestface-workflow")
                        )
    await beamline.insert()

    # Insert a facility into the database
    facility = Facility(name="NSLS-II", facility_id="nsls2",
                        fullname="National Synchrotron Light Source II",
                        pass_facility_id="NSLS-II")
    await facility.insert()

    # Insert a cycle into the database
    cycle = Cycle(name="1999-1", facility="nsls2", year="1999",
                  start_date="1999-01-01T00:00:00.000+00:00",
                  end_date="1999-06-30T00:00:00.000+00:00",
                  is_current_operating_cycle=True,
                  pass_description="January - June",
                  pass_id="111111"
                  )
    await cycle.insert()

    # Insert a proposal type into the database
    proposal_type = ProposalType(code="X", facility_id="nsls2",
                                 description="Proposal Type X",
                                 pass_id="999999",
                                 pass_description="Proposal Type X",
                                 )
    await proposal_type.insert()

    yield

    # Cleanup the database collections
    for model in models.all_models:
        print(f"dropping {model}")
        await model.get_motor_collection().drop()
        await model.get_motor_collection().drop_indexes()
