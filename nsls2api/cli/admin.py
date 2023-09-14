import typer

app = typer.Typer()

@app.command()
def status():
    print("If I was implemented I would tell you if you had god like permissions.")


