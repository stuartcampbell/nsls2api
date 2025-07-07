import pydantic


class FacilityCyclesResponseModel(pydantic.BaseModel):
    facility: str
    cycles: list[str]


class FacilityCurrentOperatingCycleResponseModel(pydantic.BaseModel):
    facility: str
    cycle: str
