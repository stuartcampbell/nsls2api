import typer
from rich.panel import Panel
from rich.table import Table

from nsls2api.models.facilities import FacilityName
from nsls2api.cli.utils.api import call_nsls2api_endpoint
from nsls2api.cli.utils.cli_helpers import auto_help_if_no_command
from nsls2api.cli.utils.console import console, error, info, warning

app = typer.Typer(invoke_without_command=True)


@app.callback()
@auto_help_if_no_command()
def facility_callback(ctx: typer.Context):
    pass  # No need to call anything manually


@app.command()
def view(facility: FacilityName):
    info(f"Viewing Facility: [green]{facility}[/green]")


@app.command()
def cycles(facility: FacilityName):
    """
    Retrieve and display a list of cycles for a facility from the API.
    """
    endpoint = f"v1/facility/{facility}/cycles"
    response = call_nsls2api_endpoint(endpoint, method="GET")

    # Expecting the API to return a list of beamlines
    if response is None:
        error(f"ERROR: Failed to retrieve cycle list for '{facility}' facility.")
        raise typer.Exit(code=1)

    cycles = response.json().get("cycles", [])

    # Get the current operating cycle
    current_cycle_response = call_nsls2api_endpoint(
        f"v1/facility/{facility}/cycles/current", method="GET"
    )
    if current_cycle_response is None:
        warning(
            f"WARNING: Failed to retrieve current operating cycle for '{facility}' facility."
        )
        # Set current_cycle to an empty string if the API call fails
        current_cycle = ""
    else:
        current_cycle = current_cycle_response.json().get("cycle", "")

    table = Table(
        title=f"Facility Cycles ({facility})",
        show_header=True,
        header_style="bold green",
    )
    table.add_column("Cycle", style="cyan", no_wrap=True)
    table.add_column("Current Cycle", style="magenta")
    # Adjust row extraction based on API response structure
    for cycle in cycles:
        # Check if the cycle is the current operating cycle
        is_current_cycle = "Yes" if cycle == current_cycle else ""
        table.add_row(cycle, is_current_cycle)
    # Wrap table in a panel for a nicer output
    panel = Panel(table, title_align="left")
    console.print(panel)
