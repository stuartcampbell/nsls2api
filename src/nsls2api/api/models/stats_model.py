import pydantic


class StatsModel(pydantic.BaseModel):
    facility_count: int
    proposal_count: int
    beamline_count: int
    commissioning_proposal_count: int


class AboutModel(pydantic.BaseModel):
    description: str
    version: str
