import typer
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from nsls2api.cli.settings import (
    ApiEnvironment,
    Config,
    ConfigKey,
    get_base_url,
)

app = typer.Typer()
console = Console(
    theme=Theme(
        {
            "info": "cyan",
            "warning": "yellow",
            "error": "red bold",
            "success": "green bold",
            "url": "blue underline",
            "env.prod": "red bold",
            "env.dev": "yellow",
            "env.local": "green",
            "env.custom": "cyan",
        }
    )
)


def create_environment_table() -> Table:
    """Create a table showing all available environments"""
    table = Table(box=ROUNDED, show_header=True)
    table.add_column("Shortcut", style="cyan bold")
    table.add_column("Environment", style="green")
    table.add_column("URL", style="blue")

    table.add_row("prod", "Production", ApiEnvironment.PRODUCTION.value)
    table.add_row("dev", "Development", ApiEnvironment.DEVELOPMENT.value)
    table.add_row("local", "Local", ApiEnvironment.LOCAL.value)

    return table


def get_environment_style(url: str) -> str:
    """Get the appropriate style for the environment"""
    if url == ApiEnvironment.PRODUCTION.value:
        return "env.prod"
    elif url == ApiEnvironment.DEVELOPMENT.value:
        return "env.dev"
    elif url == ApiEnvironment.LOCAL.value:
        return "env.local"
    else:
        return "env.custom"


def get_environment_name(url: str) -> str:
    """Get a friendly name for the environment"""
    if url == ApiEnvironment.PRODUCTION.value:
        return "Production"
    elif url == ApiEnvironment.DEVELOPMENT.value:
        return "Development"
    elif url == ApiEnvironment.LOCAL.value:
        return "Local"
    else:
        return "Custom"


@app.command()
def show():
    """Show current API environment"""
    current_url = get_base_url()
    env_name = get_environment_name(current_url)
    env_style = get_environment_style(current_url)

    # Create status table
    status_table = Table(show_header=False, box=None)
    status_table.add_column("Key", style="cyan")
    status_table.add_column("Value")

    status_table.add_row("Environment", Text(env_name, style=env_style))
    status_table.add_row("URL", Text(current_url, style="url"))

    # Create the main panel
    panel = Panel(status_table, title="Current Environment", border_style=env_style)

    # Show available environments
    env_table = create_environment_table()
    env_panel = Panel(env_table, title="Available Environments", border_style="cyan")

    console.print(panel)
    console.print("\n[info]Available Environments:")
    console.print(env_panel)


@app.command()
def switch(
    env: str = typer.Argument(
        ..., help="Environment to switch to (prod/dev/local) or a custom URL"
    ),
):
    """Switch API environment"""
    env_map = {
        "prod": ApiEnvironment.PRODUCTION.value,
        "dev": ApiEnvironment.DEVELOPMENT.value,
        "local": ApiEnvironment.LOCAL.value,
    }

    # If it's a known environment shortcut, use the mapped URL
    url = env_map.get(env.lower(), env)

    with console.status("[cyan]Switching environment...", spinner="dots"):
        Config.set_value("api", ConfigKey.BASE_URL, url)

    env_name = get_environment_name(url)
    env_style = get_environment_style(url)

    # Create result table
    result_table = Table(show_header=False, box=None)
    result_table.add_column("Key", style="cyan")
    result_table.add_column("Value")

    result_table.add_row("New Environment", Text(env_name, style=env_style))
    result_table.add_row("URL", Text(url, style="url"))

    panel = Panel(result_table, title="Environment Switched", border_style="green")

    console.print(panel)
