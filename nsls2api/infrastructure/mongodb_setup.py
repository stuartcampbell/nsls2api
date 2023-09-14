import beanie
import motor.motor_asyncio
from rich.pretty import pprint

from nsls2api import models


async def init_connection(hostname: str, port: int, db_name: str):
    conn_str = f"mongodb://{hostname}:{port}/{db_name}"
    client = motor.motor_asyncio.AsyncIOMotorClient(conn_str)

    await beanie.init_beanie(database=client[db_name], document_models=models.all_models)

    pprint(f"Connected to {db_name} on localhost.")
