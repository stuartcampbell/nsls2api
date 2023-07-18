import typer

app = typer.Typer()


@app.command()
def status():
    print("General status of NSLS-II API")


@app.command()
def metrics():
    print("General metrics of NSLS-II API")
