import pydantic


class SlackUser(pydantic.BaseModel):
    user_id: str
    username: str


class SlackPerson(SlackUser):
    email: str


class SlackBot(SlackUser):
    bot_id: str


class SlackChannel(pydantic.BaseModel):
    channel_id: str
    channel_name: str


class SlackChannelToCreate(pydantic.BaseModel):
    channel_name: str
    proposal_id: str
    beamlines: list[str] | None = None
    topic: str | None = None


class ProposalSlackChannel(SlackChannel):
    topic: str | None = None
    users: list[SlackUser] | None = None
    managers: list[SlackUser] | None = None
    bots: list[SlackBot] | None = None
    is_private: bool


class SlackChannelResponseModel(pydantic.BaseModel):
    channel_id: str
    channel_name: str
    beamline_slack_managers: list[str] | None = []
    user_ids: list[str] | None = []
    message: str | None = None


class ProposalSlackChannelList(pydantic.BaseModel):
    slack_channels: list[ProposalSlackChannel]
    count: int
