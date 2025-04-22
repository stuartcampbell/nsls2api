import httpx
import typer
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from nsls2api.cli.settings import get_base_url, get_token

app = typer.Typer(invoke_without_command=True)

@app.callback()
def users_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.command.get_help(ctx))
        raise typer.Exit()

console = Console(
    theme=Theme(
        {
            "info": "cyan",
            "warning": "yellow",
            "error": "red bold",
            "success": "green bold",
            "health.good": "green bold",
            "health.bad": "red bold",
        }
    )
)


@app.command()
def status():
    """Show general status of NSLS-II API"""
    url = f"{get_base_url()}/v1/about"

    with console.status("[cyan]Fetching API status...", spinner="dots"):
        try:
            with httpx.Client() as client:
                token = get_token()
                headers = {"Authorization": f"{token}"} if token else {}
                response = client.get(url, headers=headers)
                response.raise_for_status()
                about_data = response.json()

                # Create status table
                status_table = Table(show_header=False, box=None)
                status_table.add_column("Key", style="cyan")
                status_table.add_column("Value", style="green")

                status_table.add_row("Status", "✓ Available")
                status_table.add_row("Version", about_data["version"])
                status_table.add_row("Description", about_data["description"])
                status_table.add_row("API URL", get_base_url())

                # Add container info if available
                if "container_info" in about_data and about_data["container_info"]:
                    status_table.add_row("Container", about_data["container_info"])

                panel = Panel(
                    status_table, title="NSLS-II API Status", border_style="green"
                )
                console.print(panel)

        except httpx.HTTPStatusError as exc:
            panel = Panel(
                f"[error]HTTP Error: {exc.response.status_code} - {exc.response.reason_phrase}",
                title="API Status Error",
                border_style="red",
            )
            console.print(panel)
        except httpx.RequestError as exc:
            panel = Panel(
                f"[error]Request Error: {exc}",
                title="API Status Error",
                border_style="red",
            )
            console.print(panel)


@app.command()
def metrics():
    """Show general metrics of NSLS-II API"""
    url = f"{get_base_url()}/v1/stats"

    with console.status("[cyan]Fetching API metrics...", spinner="dots"):
        try:
            with httpx.Client() as client:
                token = get_token()
                headers = {"Authorization": f"{token}"} if token else {}
                response = client.get(url, headers=headers)
                response.raise_for_status()
                stats_data = response.json()

                # Create main metrics table
                metrics_table = Table(show_header=False, box=None)
                metrics_table.add_column("Key", style="cyan")
                metrics_table.add_column("Value", style="green")

                metrics_table.add_row(
                    "Facility Count", str(stats_data["facility_count"])
                )
                metrics_table.add_row(
                    "Beamline Count", str(stats_data["beamline_count"])
                )
                metrics_table.add_row(
                    "Proposal Count", str(stats_data["proposal_count"])
                )
                metrics_table.add_row(
                    "Commissioning Proposal Count",
                    str(stats_data["commissioning_proposal_count"]),
                )

                # Create health status table
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
                    nsls2_table.add_row(
                        cycle_data["cycle"], str(cycle_data["proposal_count"])
                    )

                # Create LBMS proposals per cycle table
                lbms_table = Table(title="LBMS Proposals Per Cycle", box=ROUNDED)
                lbms_table.add_column("Cycle", style="cyan")
                lbms_table.add_column("Proposal Count", style="green", justify="right")

                for cycle_data in stats_data["lbms_proposals_per_cycle"]:
                    lbms_table.add_row(
                        cycle_data["cycle"], str(cycle_data["proposal_count"])
                    )

                # Create main panel
                main_panel = Panel(
                    metrics_table, title="NSLS-II API Metrics", border_style="green"
                )

                # Print all panels and tables
                console.print(main_panel)
                console.print(health_table)
                console.print(nsls2_table)
                console.print(lbms_table)

        except httpx.HTTPStatusError as exc:
            panel = Panel(
                f"[error]HTTP Error: {exc.response.status_code} - {exc.response.reason_phrase}",
                title="API Metrics Error",
                border_style="red",
            )
            console.print(panel)
        except httpx.RequestError as exc:
            panel = Panel(
                f"[error]Request Error: {exc}",
                title="API Metrics Error",
                border_style="red",
            )
            console.print(panel)
