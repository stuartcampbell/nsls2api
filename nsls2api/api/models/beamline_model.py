from typing import Optional

import pydantic
from nsls2api.models.beamlines import BeamlineService


# class BeamlineService(pydantic.BaseModel):
#     name: str
#     servername: Optional[str]
#     uri: Optional[str]
#
class BeamlineServicesModel(pydantic.BaseModel):
    count: int
    services: list[BeamlineService]

#
# class BeamlineResponseModel(pydantic.BaseModel):
#     name: str
#     long_name: str
