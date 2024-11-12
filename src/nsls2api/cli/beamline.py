import typer

app = typer.Typer()


@app.command()
def view(beamline: str):
    print(f"Viewing Beamline : {beamline}")


@app.command("list")
def list_beamlines():
    print("Listing beamlines...")
