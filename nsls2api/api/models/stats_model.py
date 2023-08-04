import pydantic

class StatsModel(pydantic.BaseModel):
    facility_count: int
    proposal_count: int
    beamline_count: int