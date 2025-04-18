import typer
import requests

from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from rich.panel import Panel

from nsls2api.cli.settings import get_base_url, get_token, set_token, remove_token

app = typer.Typer()
console = Console(theme=Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold"
}))

@app.command()
def view(beamline: str):
    print(f"Viewing Beamline : {beamline}")


@app.command("list")
def list_beamlines():
    """
    Retrieve and display a list of beamlines from the API.
    """
    try:
        response = requests.get(f"{get_base_url()}/v1/beamlines")
        response.raise_for_status()
    except Exception as e:
        console.print(f"[red]Error fetching beamlines: {e}[/red]")
        raise typer.Exit(code=1)
    # Expecting the API to return a list of beamlines
    beamlines = response.json()
    table = Table(title="Beamlines")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    # Adjust row extraction based on API response structure
    for beam in beamlines:
        table.add_row(str(beam.get("port", "")), beam.get("name", ""), beam.get("long_name", ""))
    console.print(table)

@app.command("view")
def view_beamline(beamline: str):
    """
    Retrieve and display details of a specific beamline.

    Args:
        beamline (str): The identifier of the beamline.
    """
    try:
        response = requests.get(f"{get_base_url()}/v1/beamline/{beamline}")
        response.raise_for_status()
    except Exception as e:
        console.print(f"[error]Error fetching beamline details: {e}[/error]")
        raise typer.Exit(code=1)
    details = response.json()
    # Create a table with headers for fields and values
    table = Table(show_header=True, header_style="bold magenta")
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