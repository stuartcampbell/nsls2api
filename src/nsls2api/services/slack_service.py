from slack_sdk import WebClient
from slack_sdk.web.slack_response import SlackResponse
from slack_sdk.errors import SlackApiError

from nsls2api.infrastructure.config import get_settings
from nsls2api.infrastructure.logging import logger
from nsls2api.models.slack_models import SlackBot, SlackUser
from nsls2api.services import proposal_service

settings = get_settings()

class ChannelAlreadyExistsError(Exception):
    pass

def create_conversation(name: str, is_private: bool = True) -> str | None:
    """
    Creates a new Slack conversation with the given name and privacy setting.

    Args:
        name (str): The name of the conversation to be created.
        is_private (bool, optional): Whether the conversation should be private. Defaults to True.

    Returns:
        str | None: The ID of the created conversation if successful, None otherwise.

    Raises:
        ChannelAlreadyExistsError: If a channel with the given name already exists.
    """
    client = WebClient(token=settings.slack_bot_token)
    try:
        response = client.conversations_create(name=name, is_private=is_private)
        if response.get("ok"):
            return response.get("channel").get("id")
    except SlackApiError as error:
        if error.response["error"] == "name_taken":
            raise ChannelAlreadyExistsError(f"Channel '{name}' already exists.")
        else:
            logger.exception(error)
    return None


def get_bot_details() -> SlackBot:
    """
    Retrieves the details of the Slack bot.

    Returns:
        SlackBot: An instance of the SlackBot class containing the bot details.
    """
    client = WebClient(token=settings.slack_bot_token)
    response = client.auth_test()

    return SlackBot(
        username=response.get("user"),
        user_id=response.get("user_id"),
        bot_id=response.get("bot_id"),
    )


def get_channel_members(channel_id: str) -> list[str]:
    """
    Retrieves the members of a Slack channel.
    It assumes that the bot is already a member of the
    channel (if it is a private channel)

    Args:
        channel_id (str): The ID of the Slack channel.

    Returns:
        list[str]: A list of member IDs in the channel.
    """
    try:
        client = WebClient(token=settings.slack_bot_token)
        response = client.conversations_members(channel=channel_id)
    except SlackApiError as error:
        logger.exception(error)
        return []
    return response.get("members", [])


def add_bot_to_channel(channel_id: str):
    """
    Adds the bot to the specified channel.

    Args:
        channel_id (str): The ID of the channel to add the bot to.

    Raises:
        Exception: If an error occurs while adding the bot to the channel.

    Returns:
        None
    """
    bot = get_bot_details()
    client = WebClient(token=settings.superadmin_slack_user_token)
    logger.info(f"Inviting {bot.username} ({bot.user_id}) to channel {channel_id}.")
    try:
        response = client.admin_conversations_invite(
            channel_id=channel_id, user_ids=[bot.user_id]
        )
        logger.info(response)
    except SlackApiError as error:
        if error.response["error"] == "failed_for_some_users":
            channel_members = get_channel_members(channel_id)
            if "failed_user_ids" in error.response:
                if (bot.user_id in error.response["failed_user_ids"]) and (
                    bot.user_id in channel_members
                ):
                    logger.info(f"{bot.username} is already in channel {channel_id}.")
                else:
                    logger.error(
                        f"Failed to add bot {bot.username} to channel {channel_id}."
                    )
        else:
            logger.exception(error)
            raise Exception(error) from error


async def is_channel_private(channel_id: str) -> bool:
    """
    Checks if a Slack channel is private.

    Args:
        channel_id (str): The ID of the channel to check.

    Returns:
        bool: True if the channel is private, False otherwise.
    """
    client = WebClient(token=settings.slack_bot_token)
    response = client.conversations_info(channel=channel_id)
    return response.get("channel").get("is_private")


async def create_channel(
    name: str,
    is_private: bool = True,
) -> str | None:
    """
    Creates a new Slack channel with the given name and privacy settings.  If the channel
    already exists, it will convert the channel to the desired privacy setting and invite
    the necessary bot user to the channel.

    Args:
        name (str): The name of the channel to be created.
        is_private (bool, optional): Whether the channel should be private. Defaults to True.

    Returns:
        str | None: The ID of the created channel if successful, None otherwise.
    """
    super_client = WebClient(token=settings.superadmin_slack_user_token)

    # Does the channel already exist?
    channel_id = channel_id_from_name(name)

    if channel_id:
        logger.info(f"Found existing channel called {name}.")
        if is_private:
            if await is_channel_private(channel_id):
                logger.info("Channel is already private.")
            else:
                try:
                    logger.info(f"Trying to convert channel {name} to private.")
                    response = super_client.admin_conversations_convertToPrivate(
                        channel_id=channel_id
                    )
                    logger.info(
                        f"Response from converting channel to private: {response}"
                    )
                except SlackApiError as e:
                    logger.exception(f"Error converting channel to private: {e}")
                    return None
        else:
            if await is_channel_private(channel_id):
                try:
                    logger.info(f"Trying to convert channel {name} to public.")
                    response = super_client.admin_conversations_convertToPublic(
                        channel_id=channel_id
                    )
                    logger.info(
                        f"Response from converting channel to public: {response}"
                    )
                except SlackApiError as e:
                    logger.exception(f"Error converting channel to public: {e}")
                    return None

    else:
        # No pre-existing channel, so create a new one
        try:
            logger.info(f"Trying to create channel called '{name}'.")
            response = super_client.admin_conversations_create(
                name=name,
                is_private=is_private,
                team_id=settings.nsls2_workspace_team_id,
            )
            logger.info(f"Response from creating slack channel: {response}")

        except SlackApiError as e:
            logger.exception(f"Error creating channel: {e}")
            return None

    # Now lets add our 'bot' to the channel
    add_bot_to_channel(channel_id)

    return channel_id


def retrieve_private_channel_id(name: str) -> str | None:
    """
    Retrieves the channel ID for a given private channel name.

    Args:
        name (str): The name of the channel.

    Returns:
        str | None: The ID of the channel if found, None otherwise.
    """
    client = WebClient(token=settings.slack_bot_token)
    response = client.conversations_list(types="private_channel")
    # This returns a list of channels, find the one with the exact name (just in case we get more than one returned)
    for channel in response.get("channels"):
        print(f"Channel: {channel.get('name')}")
        if channel.get("name") == name:
            logger.info(f"Found existing channel '{name}' with ID {channel['id']}")
            return channel.get("id")
    return None


def lookup_user_by_email(email: str) -> SlackUser | None:
    """
    Looks up the user associated with the given email address.

    Args:
        email (str): The email address of the user.

    Returns:
        SlackUser | None: An instance of the SlackUser class containing
                          the user details if found, None otherwise.
    """
    try:
        client = WebClient(token=settings.slack_bot_token)
        response = client.users_lookupByEmail(email=email)
    if response.get("ok"):
        return SlackUser(
            user_id=response.get("user", {}).get("id", ""),
            username=response.get("user", {}).get("name", ""),
            email=email,
        )
    return None

def create_proposal_channel(proposal_id: str) -> str | None:

    # What is the name of the channel(s) associated with this proposal?
    channels_to_create = proposal_service.slack_channels_for_proposal(proposal_id)


def add_users_to_channel(channel_id: str, user_ids: list[str]):
    try:
        userlist = ",".join(user_ids)
        get_boring_app().client.conversations_invite(channel=channel_id, users=userlist)
    except SlackApiError as error:
        if error.response["error"] == "failed_for_some_users":
            channel_members = get_channel_members(channel_id)
            if "failed_user_ids" in error.response:
                for failed_user_id in error.response["failed_user_ids"]:
                    if failed_user_id in channel_members:
                        logger.info(
                            f"{failed_user_id} is already in channel {channel_id}."
                        )
                    else:
                        logger.error(
                            f"Failed to add user {failed_user_id} to channel {channel_id}."
                        )
        else:
            logger.exception(error)
            raise Exception(error) from error



