from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from .models.subject import Subject


class Database:
    _client = None

    @classmethod
    async def get_client(cls):
        if cls._client is None:
            cls._client = AsyncIOMotorClient("mongodb://localhost:27017/")
            await init_beanie(database=cls._client.my_database, document_models=[Subject])
        return cls._client


