from enum import Enum
import pydantic

class FacilityName(Enum):
    nsls2 = "nsls2"
    lbms = "lbms"
    cfn = "cfn"

class FacilityCyclesResponseModel(pydantic.BaseModel):
    facility: str
    cycles: list[str]

class FacilityCurrentOperatingCycleResponseModel(pydantic.BaseModel):
    facility: str
    cycle: str