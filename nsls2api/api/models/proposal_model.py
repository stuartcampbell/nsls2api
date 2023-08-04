import pydantic


class UsernamesModel(pydantic.BaseModel):
    usernames: list[str]
