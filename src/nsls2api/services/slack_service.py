from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from nsls2api.infrastructure.config import get_settings
from nsls2api.infrastructure.logging import logger

settings = get_settings()


def create_channel(name: str, is_private: bool = False) -> str | None:
    client = WebClient(token=settings.slack_bot_token)
    app = App(
        token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret
    )
    try:
        response = app.client.conversations_create(name=name, is_private=is_private)
        return response["channel"]["id"]
    except SlackApiError as e:
        logger.error(f"Error creating channel: {e}")
        return None


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
