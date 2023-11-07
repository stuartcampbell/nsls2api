import typer

from nsls2api.services.facility_service import facility_cycles

app = typer.Typer()


@app.command()
def view(facility: str):
    print(f"Viewing Facility: {facility}")


@app.command()
def cycles(facility: str):
    cycle_list = facility_cycles(facility)
    return cycle_list
