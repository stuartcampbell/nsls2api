import pydantic


class SlackBot(pydantic.BaseModel):
    username: str
    user_id: str
    bot_id: str


class SlackUser(pydantic.BaseModel):
    user_id: str
    username: str
    email: str


class SlackChannelCreationResponseModel(pydantic.BaseModel):
    channel_id: str
    channel_name: str
    beamline_slack_managers: list[str] | None = []
    user_ids: list[str] | None = []
    message: str | None = None
