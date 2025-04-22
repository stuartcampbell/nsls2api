from typing import Optional

import httpx
import typer
from httpx import Response
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


def call_nsls2api_endpoint(
    endpoint: str, method: str = "GET", data: dict = None
) -> Optional[Response]:
    """
    Call the NSLS-II API endpoint and return the response.
    """
    url = f"{get_base_url()}/{endpoint}"
    try:
        with httpx.Client() as client:
            token = get_token()
            headers = {"Authorization": f"{token}"} if token else {}
            if method == "GET":
                response = client.get(url, headers=headers)
            elif method == "POST":
                response = client.post(url, json=data, headers=headers)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            console.print("[red]Invalid API token[/red]")
            return None
        elif exc.response.status_code == 403:
            console.print("[red]Access denied[/red]")
            return None
        elif exc.response.status_code == 404:
            console.print(f"[red]Endpoint not found: {url}[/red]")
            return None
        else:
            console.print(
                f"[red]An error occurred while trying to contact the API: {exc}[/red]"
            )
            return None
    except httpx.RequestError as exc:
        console.print(
            f"[red]An error occurred while trying to contact the API: {exc}[/red]"
        )
        return None
    return response


@app.command("list")
def list_beamlines():
    """
    Retrieve and display a list of beamlines from the API.
    """
    endpoint = "v1/beamlines"
    response = call_nsls2api_endpoint(endpoint, method="GET")

    # Expecting the API to return a list of beamlines
    if response is None:
        console.print("[red]Failed to retrieve beamlines.[/red]")
        raise typer.Exit(code=1)
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
    endpoint = f"v1/beamline/{beamline}"
    response = call_nsls2api_endpoint(endpoint)
    if response is None:
        console.print(f"[red]Failed to retrieve details for {beamline} beamline.[/red]")
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
    endpoint = f"v1/beamline/{beamline}/detectors"
    # Call the API to get the list of detectors
    response = call_nsls2api_endpoint(endpoint)
    if response is None:
        console.print("[red]Failed to retrieve detectors.[/red]")
        raise typer.Exit(code=1)
    detectors = response.json().get("detectors", [])
    if not detectors:
        console.print(f"[warning]No detectors found for beamline: {beamline}[/warning]")
        typer.Exit()
    table = Table(title=f"Detectors for Beamline: {beamline}")
    table.add_column("Name", style="cyan")
    table.add_column("Manufacturer", style="blue")
    table.add_column("Description", style="magenta")
    table.add_column("Directory", style="magenta")
    table.add_column("Granularity", style="green")
    for detector in detectors:
        table.add_row(
            detector.get("name", ""),
            detector.get("manufacturer", ""),
            detector.get("description", "N/A"),
            detector.get("directory_name", "N/A"),
            detector.get("granularity", "N/A"),
        )
    console.print(table)
