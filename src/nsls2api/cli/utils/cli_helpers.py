import typer


def print_help_if_no_command(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.command.get_help(ctx))
        raise typer.Exit()
