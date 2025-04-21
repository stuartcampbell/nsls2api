import httpx
import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

from nsls2api.cli.settings import get_base_url, get_token

app = typer.Typer()
console = Console(
    theme=Theme(
        {
            "info": "cyan",
            "warning": "yellow",
            "error": "red bold",
            "success": "green bold",
        }
    )
)


@app.command("list")
def list_beamlines():
    """
    Retrieve and display a list of beamlines from the API.
    """
    url = f"{get_base_url()}/v1/beamlines"
    try:
        with httpx.Client() as client:
            token = get_token()
            headers = {"Authorization": f"{token}"} if token else {}
            response = client.get(url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            return False, "Invalid API token"
        elif exc.response.status_code == 403:
            return False, "Access denied"
        else:
            return False, f"An error occurred: {exc}"
    except httpx.RequestError as exc:
        console.print(
            f"[red]An error occurred while trying to contact the API: {exc}[/red]"
        )

    # Expecting the API to return a list of beamlines
    beamlines = response.json()
    table = Table(title="Beamlines", show_header=True, header_style="bold green")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    # Adjust row extraction based on API response structure
    for beam in beamlines:
        table.add_row(
            str(beam.get("port", "")), beam.get("name", ""), beam.get("long_name", "")
        )
    # Wrap table in a panel for a nicer output
    panel = Panel(table, title="All Beamlines", title_align="left")
    console.print(panel)


@app.command("view")
def view_beamline(beamline: str):
    """
    Retrieve and display details of a specific beamline.

    Args:
        beamline (str): The identifier of the beamline.
    """
    url = f"{get_base_url()}/v1/beamline/{beamline}"
    try:
        with httpx.Client() as client:
            token = get_token()
            headers = {"Authorization": f"{token}"} if token else {}
            response = client.get(url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            return False, "Invalid API token"
        elif exc.response.status_code == 403:
            return False, "Access denied"
        else:
            return False, f"An error occurred: {exc}"
    except httpx.RequestError as exc:
        console.print(
            f"[red]An error occurred while trying to contact the API: {exc}[/red]"
        )

    try:
        response = requests.get()
        response.raise_for_status()
    except Exception as e:
        console.print(f"[error]Error fetching beamline details: {e}[/error]")
        raise typer.Exit(code=1)
    details = response.json()
    # Create a table with headers for fields and values
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Field", style="blue", no_wrap=True)
    table.add_column("Value", style="white")
    for key, value in details.items():
        table.add_row(str(key), str(value))
    # Wrap table in a panel for a nicer output
    panel = Panel(table, title=f"Beamline Details: {beamline}", title_align="left")
    console.print(panel)


@app.command("detectors")
def list_detectors(beamline: str):
    """
    Retrieve and display detectors for a specific beamline.

    Args:
        beamline (str): The identifier of the beamline.
    """
    try:
        response = requests.get(f"{get_base_url()}/v1/beamline/{beamline}/detectors")
        response.raise_for_status()
    except Exception as e:
        console.print(f"[error]Error fetching detectors: {e}[/error]")
        raise typer.Exit(code=1)
    detectors = response.json().get("detectors", [])
    if not detectors:
        console.print(f"[warning]No detectors found for beamline: {beamline}[/warning]")
        return
    table = Table(title=f"Detectors for Beamline: {beamline}")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_column("Granularity", style="green")
    for detector in detectors:
        table.add_row(
            detector.get("name", ""),
            detector.get("description", "N/A"),
            detector.get("granularity", "N/A"),
        )
    console.print(table)
