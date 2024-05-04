from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from nsls2api.infrastructure.config import get_settings
from nsls2api.infrastructure.logging import logger

settings = get_settings()
app = App(token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret)


def create_channel(name: str, is_private: bool = False, description: str = None) -> str | None:
    super_client = WebClient(token=settings.superadmin_slack_user_token)
    try:
        response = super_client.admin_conversations_create(name=name, is_private=is_private, description=description,
                                                           team_id=settings.nsls2_workspace_team_id)
        # Now lets try and add our 'bot' to the channel
        created_channel_id = response.data["channel_id"]
        logger.info(f"Created channel {created_channel_id}")
        app.client.conversations_join(channel=created_channel_id)
    except SlackApiError as e:
        logger.exception(f"Error creating channel: {e}")
        return None

    return created_channel_id


def find_channel(name: str) -> str | None:
    client = WebClient(token=settings.slack_bot_token)
    app = App(
        token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret
    )
    try:
        response = app.client.conversations_list()
        for channel in response["channels"]:
            print(channel)
            if channel["name"] == name:
                return channel["id"]
        return None
    except SlackApiError as e:
        logger.error(f"Error finding channel: {e}")
        return None


def channel_id_from_name(name: str) -> str | None:
    client = WebClient(token=settings.superadmin_slack_user_token)
    response = client.admin_conversations_search(query=name)
    # This returns a list of channels, find the one with the exact name (just in case we get more than one returned)
    for channel in response["conversations"]:
        if channel["name"] == name:
            return channel["id"]


def rename_channel(name: str, new_name: str) -> str | None:
    client = WebClient(token=settings.slack_bot_token)
    channel_id = channel_id_from_name(name)
    if channel_id is None:
        raise Exception(f"Channel {name} not found.")

    response = client.conversations_rename(channel=channel_id, name=new_name)

    if response["ok"] != True:
        raise Exception(f"Failed to rename channel {name} to {new_name}")
