from typing import Optional

import pydantic

class Person(pydantic.BaseModel):
    firstname : str
    lastname: str
    email: str
    bnl_id: Optional[str]