import getpass
import httpx
import typer
from typing import Optional, Tuple

from nsls2api.cli.settings import get_base_url, get_token, set_token, remove_token
from nsls2api.infrastructure.security import SpecialUsers

app = typer.Typer()

def verify_token(token: str) -> Tuple[bool, Optional[str]]:
    """
    Verify if a token is valid by making an API call.
    Returns a tuple of (is_valid, username or error_message)
    """
    url = f"{get_base_url()}/v1/person/me"
    try:
        with httpx.Client() as client:
            headers = {"Authorization": f"{token}"}
            response = client.get(url, headers=headers)
            response.raise_for_status()
            return True, response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            return False, "Invalid API token"
        elif exc.response.status_code == 403:
            return False, "Access denied"
        else:
            return False, f"An error occurred: {exc}"
    except httpx.RequestError as exc:
        return False, f"An error occurred while trying to contact the API: {exc}"

@app.command()
def status():
    """Show the current authentication status"""
    token = get_token()
    if token is None:
        typer.echo("Not logged in. Use 'nsls2api auth login' to authenticate.")
        return

    is_valid, result = verify_token(token)
    if is_valid:
        typer.echo(f"Logged in as: {result}")
        typer.echo(f"API URL: {get_base_url()}")
    else:
        typer.echo(f"Authentication error: {result}")
        typer.echo("Use 'nsls2api auth login' to reauthenticate.")

@app.command()
def login():
    """Log in to the NSLS-II API"""
    # Let's see if there is a token in the local config file
    token = get_token()
    read_token_from_file = True
    
    if token is None:
        read_token_from_file = False
        typer.echo("No API token found")
        token = getpass.getpass(prompt="Please enter your API token:")
        if len(token) == 0:
            logged_in_username: SpecialUsers = SpecialUsers.anonymous
            typer.echo("Authenticated as anonymous")
            return

    is_valid, result = verify_token(token)
    if is_valid:
        typer.echo(f"Authenticated as {result}")
        if not read_token_from_file:
            set_token(token)
            typer.echo("Token saved to config file")
    else:
        typer.echo(result)

@app.command()
def logout():
    """Log out and remove stored credentials"""
    remove_token()
    typer.echo("Logged out successfully")