import beanie
import motor.motor_asyncio
from rich.pretty import pprint
import nsls2api.models


async def init_connection(db_name: str):
    conn_str = f"mongodb://localhost:27017/{db_name}"
    client = motor.motor_asyncio.AsyncIOMotorClient(conn_str)

    from nsls2api import models
    await beanie.init_beanie(database=client[db_name], document_models=models.all_models)

    pprint(f"Connected to {db_name} on localhost.")
