import os
from pathlib import Path
from typing import Optional

import httpx
import rich.emoji
import typer
import getpass
import configparser
from configparser import NoOptionError, NoSectionError
from nsls2api.infrastructure.security import SpecialUsers

from fastapi import requests

BASE_URL = "http://localhost:8080"

__logged_in_username = None

app = typer.Typer()


def config_from_file() -> Optional[str]:
    config = configparser.ConfigParser()
    config_userhome = os.path.expanduser("~")
    config_filepath = Path(config_userhome) / ".config" / "nsls2"
    print(f"Reading config from {config_filepath}")

    try:
        config.read(config_filepath)
        api_client_token = config.get("api", "token")
    except (NoSectionError, NoOptionError) as error:
        return None

    return api_client_token


@app.command()
def login():
    # Let's see if there is a token in the local config file ?
    token = config_from_file()
    if token is None:
        print("No API token found")
        token = getpass.getpass(prompt="Please enter your API token:")
        if len(token) == 0:
            __logged_in_username: SpecialUsers = SpecialUsers.anonymous
            print("Logged in as anonymous")
            return

    # Let's test this token
    url = f"{BASE_URL}/v1/person/me"
    try:
        with httpx.Client() as client:
            headers = {"Authorization": f"{token}"}
            response = client.get(url, headers=headers)
            response.raise_for_status()
            __logged_in_username = response.json()
            # nsls2api.cli.__logged_in_username = response.json()
            # LOGGED_IN_USERNAME = response.json()
    except httpx.RequestError as exc:
        print(f"An error occurred while trying to login {exc}")
        raise

    print("Logging in...")


@app.command()
def logout():
    print("Logging you out...")


@app.command()
def status():
    print(
        f"You might be logged in as {__logged_in_username} or {LOGGED_IN_USERNAME}, or you might not be - {rich.emoji.Emoji('person_shrugging')}"
    )
