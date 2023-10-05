import beanie
import motor.motor_asyncio
from pydantic import MongoDsn
from rich.pretty import pprint

from nsls2api import models


async def init_connection(mongodb_dsn: MongoDsn):

    pprint(f"Attempting to connect to {str(mongodb_dsn)}")

    client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_dsn, uuidRepresentation="standard")
    await beanie.init_beanie(database=client.get_default_database(), document_models=models.all_models)

    pprint(f"Connected to {client.get_default_database().name} on localhost.")
