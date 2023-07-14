from nsls2api.models.beamlines import Beamline

async def beamline_count() -> int:
    return await Beamline.count()

