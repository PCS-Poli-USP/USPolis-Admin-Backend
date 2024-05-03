from typing import Self

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from server.config import CONFIG
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User


class DatabaseSingleton:
    _instance: Self | None = None

    def __new__(cls) -> "DatabaseSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def init_connection(self) -> None:
        self.db: AsyncIOMotorDatabase = AsyncIOMotorClient(CONFIG.mongo_uri)[
            CONFIG.mongo_db_name
        ]
        await init_beanie(self.db, document_models=[User, Building])

    def get_instance(self) -> AsyncIOMotorDatabase:
        return self.db


database_singleton = DatabaseSingleton()
