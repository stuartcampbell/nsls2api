import typer

app = typer.Typer()


@app.command()
def view(beamline: str):
    print(f"Viewing Beamline : {beamline}")


@app.command()
def list():
    print(f"Listing beamlines...")
