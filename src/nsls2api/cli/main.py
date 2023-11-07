import typer

from nsls2api.cli import admin
from nsls2api.cli import api
from nsls2api.cli import auth
from nsls2api.cli import beamline
from nsls2api.cli import facility
from nsls2api.cli import proposal


app = typer.Typer()
app.add_typer(admin.app, name="admin", help="Do powerful admin level magic")
app.add_typer(api.app, name="api", help="Make NSLS-II API request")
app.add_typer(auth.app, name="auth", help="Stuff about security and fun")
app.add_typer(beamline.app, name="beamline", help="Stuff about Beamlines")
app.add_typer(facility.app, name="facility", help="Stuff about Facilities")
app.add_typer(proposal.app, name="proposal", help="Stuff about Proposals")



if __name__ == "__main__":
    app()
