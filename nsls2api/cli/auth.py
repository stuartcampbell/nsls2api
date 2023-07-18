import rich.emoji
import typer

app = typer.Typer()


@app.command()
def login():
    print("Logging in...")


@app.command()
def logout():
    print("Logging you out...")


@app.command()
def status():
    print(f"You might be logged in, or you might not be - {rich.emoji.Emoji('person_shrugging')}")
