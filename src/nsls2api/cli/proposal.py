import typer
from rich import box
from rich.panel import Panel
from rich.table import Table

from nsls2api.cli.utils.api import call_nsls2api_endpoint
from nsls2api.cli.utils.cli_helpers import auto_help_if_no_command
from nsls2api.cli.utils.console import console, error
from nsls2api.models.proposals import ProposalDisplay

app = typer.Typer(invoke_without_command=True)


@app.callback()
@auto_help_if_no_command()
def proposal_callback(ctx: typer.Context):
    pass  # No need to call anything manually


def display_proposal(proposal: ProposalDisplay):
    # --- Header Panel ---
    header_table = Table.grid(padding=(0, 2))
    header_table.add_column(justify="right", style="bold cyan")
    header_table.add_column()

    header_table.add_row("Proposal ID", proposal.proposal_id)
    header_table.add_row("Data Session", proposal.data_session)
    if proposal.title:
        header_table.add_row("Title", proposal.title)
    if proposal.type:
        header_table.add_row("Proposal Type", proposal.type)

    console.print(
        Panel(header_table, title="📋 Proposal Overview", expand=True, box=box.ROUNDED)
    )

    # --- Instruments and Cycles ---
    if proposal.instruments or proposal.cycles:
        ic_table = Table(expand=True, box=box.SIMPLE_HEAVY)
        ic_table.add_column("🔬 Instruments", style="green")
        ic_table.add_column("🔁 Cycles", style="blue")

        max_len = max(len(proposal.instruments or []), len(proposal.cycles or []))
        for i in range(max_len):
            inst = (
                proposal.instruments[i] if i < len(proposal.instruments or []) else ""
            )
            cyc = proposal.cycles[i] if i < len(proposal.cycles or []) else ""
            ic_table.add_row(inst, cyc)

        console.print(
            Panel(
                ic_table, expand=True, title="🧪 Instruments & Cycles", box=box.ROUNDED
            )
        )

    # Users 👤
    if proposal.users:
        user_table = Table(expand=True)
        user_table.add_column("Name")
        user_table.add_column("Email", style="cyan")
        user_table.add_column("BNL ID", style="magenta")
        user_table.add_column("Username", style="green")
        user_table.add_column("PI", style="bold yellow")

        for user in proposal.users:
            full_name = f"👤 {user.first_name or ''} {user.last_name or ''}".strip()
            user_table.add_row(
                full_name or "-",
                user.email,
                user.bnl_id or "-",
                user.username or "-",
                "✅" if user.is_pi else "",
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

    # --- Metadata Panel ---
    metadata_table = Table.grid(padding=(0, 2))
    metadata_table.add_column(justify="right", style="dim")
    metadata_table.add_column()

    metadata_table.add_row(
        "🕒 Created", proposal.created_on.strftime("%Y-%m-%d %H:%M:%S")
    )
    metadata_table.add_row(
        "📝 Last Updated", proposal.last_updated.strftime("%Y-%m-%d %H:%M:%S")
    )

    console.print(
        Panel(
            metadata_table,
            title="📌 Metadata",
            style="dim",
            expand=False,
            box=box.ROUNDED,
        )
    )


@app.command()
def view(
    identifier: str, saf: bool = typer.Option(False, help="Treat identifier as SAF ID")
):
    lookup_type = "SAF ID" if saf else "Proposal ID"

    if saf:
        url = f"v1/proposal/saf/{identifier}"
    else:
        url = f"v1/proposal/{identifier}"

    response = call_nsls2api_endpoint(url, method="GET")

    if response is None:
        error(f"Failed to retrieve proposal with {lookup_type} = {identifier}.")
        raise typer.Exit(code=1)

    proposal_data = response.json().get("proposal", None)
    if not proposal_data:
        error(f"No data found for proposal with {lookup_type} = {identifier}.")
        raise typer.Exit(code=1)

    # Assuming Proposal is a Pydantic model
    proposal = ProposalDisplay(**proposal_data)
    display_proposal(proposal)
