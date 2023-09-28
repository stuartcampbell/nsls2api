import pydantic


class PassCycle(pydantic.BaseModel):
    """
    This class represents PASS's representation of a Cycle.
    """

    Active: bool
    ID: int
    Year: int
    Start_Date: str
    End_Date: str
    Name: str
    Description: str
    User_Facility_ID: str

