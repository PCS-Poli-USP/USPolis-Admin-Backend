from typing import Self

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from server.config import CONFIG


class DatabaseSingleton:
    _instance: Self | None = None

    def __new__(cls) -> "DatabaseSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def init_connection(self) -> None:
        self.db: AsyncIOMotorDatabase = AsyncIOMotorClient(CONFIG.mongo_uri)[
            CONFIG.mongo_db_name
        ]

    def get_instance(self) -> AsyncIOMotorDatabase:
        return self.db


database_singleton = DatabaseSingleton()
