import os
from dotenv import load_dotenv

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from database.models.subject import Subject
from database.models.user_building import Building, User


class Database:
    _client = None

    @classmethod
    async def get_client(cls):
        if "CONN_STR" not in os.environ or "DB_NAME" not in os.environ:
            load_dotenv()

        if cls._client is None:
            cls._client = AsyncIOMotorClient(os.getenv("CONN_STR"))
            await init_beanie(database=cls._client[os.getenv("DB_NAME")], document_models=[Subject, User, Building])
        return cls._client
