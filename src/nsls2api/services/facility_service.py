import datetime
from nsls2api.api.models.facility_model import FacilityName
from nsls2api.infrastructure.logging import logger

from typing import Optional

from beanie import UpdateResponse
from beanie.operators import AddToSet, Set
from beanie.odm.operators.find.comparison import In

from nsls2api.models.cycles import Cycle
from nsls2api.models.facilities import Facility
from nsls2api.models.pass_models import PassCycle
from nsls2api.services import facility_service, pass_service


async def facilities_count() -> int:
    """
    Count the number of facilities in the database.

    :return: The number of facilities.
    """
    return await Facility.count()


async def facility_cycles(facility: str) -> Optional[list[str]]:
    """
    Facility Cycles

    This method retrieves the cycles for a given facility.

    :param facility: The facility name (str).
    :return: A list of cycles for the facility (list[Cycle]).
    """
    # FIXME: This next line is not returning a sorted list of cycles.
    cycles = (
        await Cycle.find(Cycle.facility == facility)
        .sort(+Cycle.year, +Cycle.name)
        .to_list()
    )
    cycle_list = [c.name for c in cycles if c.name is not None]
    return cycle_list


async def facility_by_pass_id(pass_user_facility_id: str) -> Optional[Facility]:
    """
    Facility by PASS ID

    This method retrieves the facility by the PASS ID.

    :param pass_id: The PASS ID (str).
    :return: The facility (Facility) or None if no facility is found.
    """
    return await Facility.find_one(Facility.pass_facility_id == pass_user_facility_id)


async def pass_id_for_facility(facility_name: str) -> Optional[str]:
    """
    PASS ID for Facility

    This method retrieves the PASS ID for a given facility.

    :param facility: The facility name (str). e.g. "nsls2, lbms, cfn, etc."
    :return: The PASS ID (str) or None if no facility is found.
    """
    facility = await Facility.find_one(Facility.facility_id == facility_name)
    if facility is None:
        return None

    return facility.pass_facility_id


async def data_roles_by_user(username: str) -> Optional[list[str]]:
    facilities = await Facility.find(In(Facility.data_admins, [username])).to_list()
    facility_names = [f.facility_id for f in facilities if f.facility_id is not None]
    return facility_names


async def current_operating_cycle(facility: str) -> Optional[str]:
    """
    Current Operating Cycle

    This method retrieves the current operating cycle for a given facility.

    :param facility: The facility name (str).
    :return: The current operating cycle (str) or None if no current operating cycle is found.
    """
    cycle = await Cycle.find_one(
        Cycle.facility == facility,
        Cycle.is_current_operating_cycle == True,  # noqa: E712
    )

    if cycle is None:
        return None

    return cycle.name


async def is_healthy(facility: str) -> bool:
    """
    Database Health Check

    This method checks the health of the information in the database.
    Basically, is the database populated with the correct information?
    e.g. Is there only one current operating cycle for a facility?

    :param facility: The facility name (str).
    :return: True if the database is healthy, False otherwise.
    """

    # Let's start with assuming the database is healthy.
    health_status = True

    logger.info(f"Checking the health of the {facility} facility data.")

    # TODO: Check that the facility exists in the database.

    # Check that there is only one current operating cycle for the facility.
    cycles = await Cycle.find(Cycle.is_current_operating_cycle == facility).to_list()
    if len(cycles) > 1:
        logger.warning(
            f"There is more than one current operating cycle for the {facility}."
        )
        health_status = False
    elif len(cycles) == 0:
        logger.warning(f"There is not an operating cycle for the {facility}.")
        health_status = False

    return health_status


async def worker_synchronize_cycles_from_pass(
    facility_name: FacilityName = FacilityName.nsls2,
) -> None:
    """
    This method synchronizes the cycles for a facility from PASS.

    :param facility: The facility name (FacilityName).
    """
    start_time = datetime.datetime.now()

    try:
        pass_cycles: PassCycle = await pass_service.get_cycles(facility_name)
    except pass_service.PassException as error:
        error_message = f"Error retrieving cycle information from PASS for {facility_name} facility."
        logger.exception(error_message)
        raise Exception(error_message) from error

    for pass_cycle in pass_cycles:
        facility = await facility_service.facility_by_pass_id(
            pass_cycle.User_Facility_ID
        )

        logger.info(f"Processing cycle: {pass_cycle.Name} for {facility.name}.")

        cycle = Cycle(
            name=pass_cycle.Name,
            accepting_proposals=pass_cycle.Active,
            facility=facility.facility_id,
            year=str(pass_cycle.Year),
            start_date=pass_cycle.Start_Date,
            end_date=pass_cycle.End_Date,
            pass_description=pass_cycle.Description,
            pass_id=str(pass_cycle.ID),
        )

        updated_cycle = await Cycle.find_one(Cycle.name == pass_cycle.Name).upsert(
            Set(
                {
                    Cycle.accepting_proposals: cycle.accepting_proposals,
                    Cycle.facility: cycle.facility,
                    Cycle.pass_description: cycle.pass_description,
                    Cycle.pass_id: cycle.pass_id,
                    Cycle.year: cycle.year,
                    Cycle.start_date: cycle.start_date,
                    Cycle.end_date: cycle.end_date,
                    Cycle.last_updated: datetime.datetime.now(),
                }
            ),
            on_insert=cycle,
            response_type=UpdateResponse.NEW_DOCUMENT,
        )

        # Now let's update the list of proposals for this cycle
        proposals_list = await pass_service.get_proposals_allocated_by_cycle(cycle.name)
        for proposal in proposals_list:
            await updated_cycle.update(
                AddToSet({Cycle.proposals: str(proposal.Proposal_ID)})
            )
            updated_cycle.last_updated = datetime.datetime.now()
            await updated_cycle.save()

    time_taken = datetime.datetime.now() - start_time
    logger.info(
        f"Cycle information (for {facility.name}) synchronized in {time_taken.total_seconds():,.2f} seconds"
    )
