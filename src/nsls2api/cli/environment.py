import typer
from nsls2api.cli.settings import (
    ApiEnvironment,
    Config,
    ConfigKey,
    get_base_url,
)

app = typer.Typer()

@app.command()
def show():
    """Show current API environment"""
    current_url = get_base_url()
    if current_url == ApiEnvironment.PRODUCTION.value:
        typer.echo(f"Current environment: production ({current_url})")
    elif current_url == ApiEnvironment.DEVELOPMENT.value:
        typer.echo(f"Current environment: development ({current_url})")
    elif current_url == ApiEnvironment.LOCAL.value:
        typer.echo(f"Current environment: local ({current_url})")
    else:
        typer.echo(f"Current environment: custom ({current_url})")

@app.command()
def switch(
    env: str = typer.Argument(
        ...,
        help="Environment to switch to (prod/dev/local) or a custom URL"
    )
):
    """Switch API environment"""
    env_map = {
        "prod": ApiEnvironment.PRODUCTION.value,
        "dev": ApiEnvironment.DEVELOPMENT.value,
        "local": ApiEnvironment.LOCAL.value,
    }
    
    url = env_map.get(env.lower(), env)
    Config.set_value("api", ConfigKey.BASE_URL, url)
    typer.echo(f"API URL set to: {url}")