import typer

from nsls2api.cli.utils.cli_helpers import auto_help_if_no_command

app = typer.Typer(invoke_without_command=True)


@app.callback()
@auto_help_if_no_command()
def admin_callback(ctx: typer.Context):
    pass  # No need to call anything manually


@app.command()
def status():
    print("If I was implemented I would tell you if you had god like permissions.")
