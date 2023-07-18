import typer

import api
import auth
import beamline
import facility
import proposal

app = typer.Typer()
app.add_typer(api.app, name="api", help="Make NSLS-II API request")
app.add_typer(auth.app, name="auth", help="Stuff about security and fun")
app.add_typer(beamline.app, name="beamline", help="Stuff about Beamlines")
app.add_typer(facility.app, name="facility", help="Stuff about Facilities")
app.add_typer(proposal.app, name="proposal", help="Stuff about Proposals")

if __name__ == "__main__":
    app()
