import os
from dotenv import load_dotenv

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from database.models.subject import Subject
from database.models.user_building import Building, User
from database.models.holiday_category import HolidayCategory
from database.models.holiday import Holiday
from database.models.classroom import Classroom
from database.models.university_class import Class
from database.models.schedule import Schedule
from database.models.reservation import Reservation
from database.models.institutional_event import InstitutionalEvent


class Database:
    _client = None

    @classmethod
    async def get_client(cls):
        if "CONN_STR" not in os.environ or "DB_NAME" not in os.environ:
            load_dotenv()

        if cls._client is None:
            cls._client = AsyncIOMotorClient(os.getenv("CONN_STR"))
            await init_beanie(database=cls._client[os.getenv("DB_NAME")], document_models=[Subject, User, Building, HolidayCategory, Holiday, Classroom, Class, Schedule, Reservation, InstitutionalEvent])
        return cls._client
