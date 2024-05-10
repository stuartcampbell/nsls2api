import pydantic

class SlackBot(pydantic.BaseModel):
    username: str
    user_id: str
    bot_id: str
