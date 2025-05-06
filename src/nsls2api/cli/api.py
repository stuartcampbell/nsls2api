import typer
from rich.box import ROUNDED
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nsls2api.cli.settings import get_base_url
from nsls2api.cli.utils.api import call_nsls2api_endpoint
from nsls2api.cli.utils.cli_helpers import auto_help_if_no_command
from nsls2api.cli.utils.console import console

app = typer.Typer(invoke_without_command=True)


@app.callback()
@auto_help_if_no_command()
def api_callback(ctx: typer.Context):
    pass  # No need to call anything manually


@app.command()
def status():
    """Show the general status of NSLS-II API"""

    with console.status("[info]Fetching API status...", spinner="dots"):
        endpoint = "v1/about"
        response = call_nsls2api_endpoint(endpoint, method="GET")

        if response is None:
            panel = Panel(
                "[error]Failed to retrieve API status. Please check your connection or API endpoint.[/error]",
                title="API Status Error",
                border_style="red",
            )
            console.print(panel)
            raise typer.Exit(code=1)

        about_data = response.json()

        # Create a status table
        status_table = Table(show_header=False, box=None)
        status_table.add_column("Key", style="cyan")
        status_table.add_column("Value", style="green")

        status_table.add_row("Status", "✓ Available")
        status_table.add_row("Version", about_data["version"])
        status_table.add_row("Description", about_data["description"])
        status_table.add_row("API URL", get_base_url())

        # Add container info if available
        if about_data.get("container_info"):
            status_table.add_row("Container", about_data["container_info"])

        panel = Panel(status_table, title="NSLS-II API Status", border_style="green")
        console.print(panel)


@app.command()
def metrics():
    """Show general metrics of NSLS-II API"""

    with console.status("[info]Fetching API metrics...", spinner="dots"):
        endpoint = "v1/stats"
        response = call_nsls2api_endpoint(endpoint, method="GET")

        if response is None:
            panel = Panel(
                "[error]Failed to retrieve API metrics. Please check your connection or API endpoint.[/error]",
                title="API Metrics Error",
                border_style="red",
            )
            console.print(panel)
            raise typer.Exit(code=1)

        stats_data = response.json()

        # Create main metrics table
        metrics_table = Table(show_header=False, box=None)
        metrics_table.add_column("Key", style="cyan")
        metrics_table.add_column("Value", style="green")

        metrics_table.add_row("Facility Count", str(stats_data["facility_count"]))
        metrics_table.add_row("Beamline Count", str(stats_data["beamline_count"]))
        metrics_table.add_row("Proposal Count", str(stats_data["proposal_count"]))
        metrics_table.add_row(
            "Commissioning Proposal Count",
            str(stats_data["commissioning_proposal_count"]),
        )

        # Create a health status table
        health_table = Table(title="Data Health Status", box=ROUNDED)
        health_table.add_column("Facility", style="cyan")
        health_table.add_column("Status", style="green")

        nsls2_health = stats_data["nsls2_data_health"]
        lbms_health = stats_data["lbms_data_health"]

        health_table.add_row(
            "NSLS-II",
            Text(
                "✓ Healthy" if nsls2_health else "✗ Unhealthy",
                style="health.good" if nsls2_health else "health.bad",
            ),
        )
        health_table.add_row(
            "LBMS",
            Text(
                "✓ Healthy" if lbms_health else "✗ Unhealthy",
                style="health.good" if lbms_health else "health.bad",
            ),
        )

        # Create NSLS-II proposals per cycle table
        nsls2_table = Table(title="NSLS-II Proposals Per Cycle", box=ROUNDED)
        nsls2_table.add_column("Cycle", style="cyan")
        nsls2_table.add_column("Proposal Count", style="green", justify="right")

        for cycle_data in stats_data["nsls2_proposals_per_cycle"]:
            nsls2_table.add_row(cycle_data["cycle"], str(cycle_data["proposal_count"]))

        # Create LBMS proposals per cycle table
        lbms_table = Table(title="LBMS Proposals Per Cycle", box=ROUNDED)
        lbms_table.add_column("Cycle", style="cyan")
        lbms_table.add_column("Proposal Count", style="green", justify="right")

        for cycle_data in stats_data["lbms_proposals_per_cycle"]:
            lbms_table.add_row(cycle_data["cycle"], str(cycle_data["proposal_count"]))

        # Create the main panel
        main_panel = Panel(
            metrics_table, title="NSLS-II API Metrics", border_style="green"
        )

        # Print all panels and tables
        console.print(main_panel)
        console.print(health_table)
        console.print(nsls2_table)
        console.print(lbms_table)
