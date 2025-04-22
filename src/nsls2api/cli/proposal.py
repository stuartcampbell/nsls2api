import typer
from rich.panel import Panel
from rich.table import Table

from nsls2api.cli.utils.api import call_nsls2api_endpoint
from nsls2api.cli.utils.cli_helpers import auto_help_if_no_command
from nsls2api.cli.utils.console import console
from nsls2api.models.proposals import ProposalDisplay

app = typer.Typer(invoke_without_command=True)


@app.callback()
@auto_help_if_no_command()
def proposal_callback(ctx: typer.Context):
    pass  # No need to call anything manually


def display_proposal(proposal: ProposalDisplay):
    # Header Panel
    header_text = f"[bold cyan]Proposal ID:[/] {proposal.proposal_id}\n"
    header_text += f"[bold cyan]Data Session:[/] {proposal.data_session}\n"
    if proposal.title:
        header_text += f"[bold cyan]Title:[/] {proposal.title}\n"
    if proposal.type:
        header_text += f"[bold cyan]Type:[/] {proposal.type}\n"
    if proposal.pass_type_id:
        header_text += f"[bold cyan]Pass Type ID:[/] {proposal.pass_type_id}"

    console.print(Panel(header_text, title="Proposal Overview", expand=False))

    # Instruments and Cycles
    if proposal.instruments or proposal.cycles:
        table = Table(title="Instruments & Cycles", expand=True)
        table.add_column("🔬Instruments", style="green")
        table.add_column("Cycles", style="blue")
        max_len = max(len(proposal.instruments or []), len(proposal.cycles or []))
        for i in range(max_len):
            inst = (
                proposal.instruments[i] if i < len(proposal.instruments or []) else ""
            )
            cyc = proposal.cycles[i] if i < len(proposal.cycles or []) else ""
            table.add_row(inst, cyc)
        console.print(table)

    # Users 👤
    if proposal.users:
        user_table = Table(expand=True)
        user_table.add_column("Name")
        user_table.add_column("Email", style="cyan")
        user_table.add_column("BNL ID", style="magenta")
        user_table.add_column("Username", style="green")
        user_table.add_column("PI", style="bold yellow")

        for user in proposal.users:
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            user_table.add_row(
                full_name or "-",
                user.email,
                user.bnl_id or "-",
                user.username or "-",
                "⭐️ PI" if user.is_pi else "",
            )

        console.print(Panel(user_table, title="👥 Proposal Users", expand=True))

    # SAFs 📎
    if proposal.safs:
        saf_table = Table(expand=True)
        saf_table.add_column("SAF ID")
        saf_table.add_column("Status")
        saf_table.add_column("🔬Instruments")

        for saf in proposal.safs:
            instruments_str = ", ".join(saf.instruments) if saf.instruments else "-"
            status_icon = (
                "🟢"
                if saf.status.lower() == "approved"
                else "🟡"
                if saf.status.lower() == "pending"
                else "🔴"
            )
            saf_table.add_row(
                saf.saf_id, f"{status_icon} {saf.status}", instruments_str
            )

        console.print(Panel(saf_table, title="📎 Safety Forms", expand=True))

    # Slack Channels 💬
    if proposal.slack_channels:
        slack_table = Table(expand=True)
        slack_table.add_column("Channel Name", style="cyan")
        slack_table.add_column("Channel ID", style="dim")

        for sc in proposal.slack_channels:
            slack_table.add_row(f"#{sc.channel_name}", sc.channel_id)

        console.print(Panel(slack_table, title="💬 Slack Integration", expand=True))

    # Metadata
    metadata_text = (
        f"[dim]Created on:[/] {proposal.created_on.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"[dim]Last updated:[/] {proposal.last_updated.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    console.print(Panel(metadata_text, title="Metadata", style="dim", expand=False))


@app.command()
def view(proposal_id: int):
    print(f"Viewing Proposal: {proposal_id}")

    url = f"v1/proposal/{proposal_id}"
    response = call_nsls2api_endpoint(url, method="GET")

    if response is None:
        print(f"ERROR: Failed to retrieve proposal {proposal_id}.")
        raise typer.Exit(code=1)

    proposal_data = response.json().get("proposal", {})
    if not proposal_data:
        print(f"ERROR: No data found for proposal {proposal_id}.")
        raise typer.Exit(code=1)

    # Assuming Proposal is a Pydantic model
    proposal = ProposalDisplay(**proposal_data)
    display_proposal(proposal)


# @app.command()
# def search(proposal: int):
#     print(f"Searching for Proposal: {proposal}")
#     with Progress(
#         SpinnerColumn(),
#         TextColumn("[progress.description]{task.description}"),
#         transient=True,
#     ) as progress:
#         progress.add_task(description="Searching...", total=None)
#         time.sleep(3)
#     print(f"Now showing all the awesome information about proposal {proposal}!")
