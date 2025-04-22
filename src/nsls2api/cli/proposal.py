import time

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer()

app = typer.Typer(invoke_without_command=True)

@app.callback()
def users_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.command.get_help(ctx))
        raise typer.Exit()

@app.command()
def view(proposal: int):
    print(f"Viewing Proposal: {proposal}")


@app.command()
def search(proposal: int):
    print(f"Searching for Proposal: {proposal}")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Searching...", total=None)
        time.sleep(3)
    print(f"Now showing all the awesome information about proposal {proposal}!")
