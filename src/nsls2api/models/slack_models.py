from typing import List

import pydantic


class SlackBot(pydantic.BaseModel):
    username: str
    user_id: str
    bot_id: str


class SlackUser(pydantic.BaseModel):
    user_id: str
    username: str
    email: str

class SlackChannel(pydantic.BaseModel):
    channel_id: str
    channel_name: str
    users: List[SlackUser]
    created: bool
    is_private: bool

class SlackChannelResponseModel(pydantic.BaseModel):
    channel_id: str
    channel_name: str
    beamline_slack_managers: list[str] | None = []
    user_ids: list[str] | None = []
    message: str | None = None

class SlackChannelResponseModelList(pydantic.BaseModel):
    slack_channels: list[SlackChannelResponseModel]
    count: int
