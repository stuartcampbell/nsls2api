from nsls2api.models.facilities import Facility


async def facilities_count() -> int:
    return await Facility.count()
