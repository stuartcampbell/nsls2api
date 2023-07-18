from typing import Optional

from nsls2api.models.beamlines import Beamline


async def beamline_count() -> int:
    return await Beamline.count()


async def beamline_by_name(name: str) -> Optional[Beamline]:
    # TODO: check that the input name looks sensible
    # TODO: make this case insensitive
    beamline = await Beamline.find_one(Beamline.name == name)
    return beamline

