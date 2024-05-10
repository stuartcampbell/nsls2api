from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from nsls2api.infrastructure.config import get_settings
from nsls2api.infrastructure.logging import logger
from nsls2api.models.slack_models import SlackBot

settings = get_settings()
app = App(token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret)
super_app = App(token=settings.superadmin_slack_user_token, signing_secret=settings.slack_signing_secret)

def get_bot_details() -> SlackBot:
    response = app.client.auth_test()

    return SlackBot(
        username=response.data["user"],
        user_id=response.data["user_id"],
        bot_id=response.data["bot_id"],
    )


def add_bot_to_channel(channel_name: str):
    bot = get_bot_details()
    channel_id = channel_id_from_name(channel_name)
    client = WebClient(token=settings.superadmin_slack_user_token)
    logger.info(f"Inviting {bot.username} ({bot.user_id}) to channel {channel_id}.")
    try:
        response = client.admin_conversations_invite(channel_id=channel_id, user_ids=[bot.user_id])
        logger.info(response)
    except SlackApiError as error:
        logger.error(error)


async def create_channel(
    name: str, is_private: bool = False, description: str = None
) -> str | None:
    super_client = WebClient(token=settings.superadmin_slack_user_token)

    # Does the channel already exist?
    channel_id = channel_id_from_name(name)
    
    if channel_id:
        logger.info(f"Found existing channel called {name}.")
    else:
        try:
            logger.info(f"Trying to create channel called '{name}'.")
            response = super_client.admin_conversations_create(
                name=name,
                is_private=is_private,
                description=description,
                team_id=settings.nsls2_workspace_team_id,
            )
            logger.info(f"Response from creating slack channel: {response}")

        except SlackApiError as e:
            logger.exception(f"Error creating channel: {e}")
            return None

    # Now lets add our 'bot' to the channel
    add_bot_to_channel(name)

    return channel_id


def channel_id_from_name(name: str) -> str | None:
    client = WebClient(token=settings.superadmin_slack_user_token)
    response = client.admin_conversations_search(query=name)
    # This returns a list of channels, find the one with the exact name (just in case we get more than one returned)
    for channel in response["conversations"]:
        if channel["name"] == name:
            return channel["id"]


def rename_channel(name: str, new_name: str) -> str | None:
    channel_id = channel_id_from_name(name)
    if channel_id is None:
        raise Exception(f"Channel {name} not found.")

    response = app.client.conversations_rename(channel=channel_id, name=new_name)

    if response.data["ok"] is not True:
        raise Exception(f"Failed to rename channel {name} to {new_name}")


def lookup_userid_by_email(email: str) -> str | None:
    response = app.client.users_lookupByEmail(email=email)
    if response.data["ok"] is True:
        return response.data["user"]["id"]


def lookup_username_by_email(email: str) -> str | None:
    response = app.client.users_lookupByEmail(email=email)
    if response.data["ok"] is True:
        return response.data["user"]["name"]

