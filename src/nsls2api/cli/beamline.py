import typer
from rich.panel import Panel
from rich.table import Table

from nsls2api.cli.utils.api import call_nsls2api_endpoint
from nsls2api.cli.utils.console import console, error

app = typer.Typer(invoke_without_command=True)

@app.callback()
def users_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.command.get_help(ctx))
        raise typer.Exit()

@app.command("list")
def list_beamlines():
    """
    Retrieve and display a list of beamlines from the API.
    """
    endpoint = "v1/beamlines"
    response = call_nsls2api_endpoint(endpoint, method="GET")

    # Expecting the API to return a list of beamlines
    if response is None:
        error("ERROR: Failed to retrieve beamlines.")
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
