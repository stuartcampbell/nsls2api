from enum import StrEnum

import pydantic


class FacilityName(StrEnum):
    nsls2 = "nsls2"
    lbms = "lbms"
    cfn = "cfn"


class FacilityCyclesResponseModel(pydantic.BaseModel):
    facility: str
    cycles: list[str]


class FacilityCurrentOperatingCycleResponseModel(pydantic.BaseModel):
    facility: str
    cycle: str


class FacilityCycleResponseModel(pydantic.BaseModel):
    facility: str
    cycle: str
    start_date: str
    end_date: str
    is_current_operating_cycle: bool
    active: bool