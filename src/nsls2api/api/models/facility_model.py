from enum import StrEnum
import pydantic

class FacilityName(StrEnum):
    nsls2 = "nsls2"
    lbms = "lbms"
    cfn = "cfn"

class UpsFacilityName(StrEnum):
    nsls2 = "nsls2"
    aps = "aps"
    lcls = "lcls"

class FacilityCyclesResponseModel(pydantic.BaseModel):
    facility: str
    cycles: list[str]

class FacilityCurrentOperatingCycleResponseModel(pydantic.BaseModel):
    facility: str
    cycle: str