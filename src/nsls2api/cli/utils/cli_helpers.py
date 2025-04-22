from functools import wraps

import typer


def auto_help_if_no_command():
    def decorator(func):
        @wraps(func)
        def wrapper(ctx: typer.Context, *args, **kwargs):
            if ctx.invoked_subcommand is None:
                typer.echo(ctx.command.get_help(ctx))
                raise typer.Exit()
            return func(ctx, *args, **kwargs)

        return wrapper

    return decorator


def print_help_if_no_command(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.command.get_help(ctx))
        raise typer.Exit()
