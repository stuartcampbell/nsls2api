import beanie
import motor.motor_asyncio
from rich.pretty import pprint

from nsls2api import models


async def init_connection(hostname: str, port: int, db_name: str, username: str = None, password: str = None):
    if (username is not None) and (password is not None):
        conn_str = f"mongodb://{username}:{password}@{hostname}:{port}/{db_name}"
    else:
        conn_str = f"mongodb://{hostname}:{port}/{db_name}"
    client = motor.motor_asyncio.AsyncIOMotorClient(conn_str, uuidRepresentation="standard")

    await beanie.init_beanie(database=client[db_name], document_models=models.all_models)

    pprint(f"Connected to {db_name} on localhost.")
