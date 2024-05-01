import asyncio
import sys
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import Document, Indexed, init_beanie

from database.models.schedule import Recurrence, Schedule, WeekDay
from database.models.university_class import Class, Preferences

current_directory = os.getcwd()
print(current_directory)
parent_directory = os.path.abspath(current_directory)
sys.path.append(parent_directory)

from database.models.subject import Subject
from database.mongo import Database


async def create_subject():
    client = await Database.get_client()

    portuguese_subject = Subject(
        subject_code="Teste",
        name="Portugues",
        professors=["Eu"],
        type="pratica",
        class_credit=2,
        work_credit=5,
        activation=datetime(2024, 2, 2),
        desactivation=datetime(2025, 2, 2),
    )

    portuguese_class = Class(
        subject=portuguese_subject,  # type: ignore
        period=["2024.2"],
        class_type="pratica",
        start_date=datetime(2024, 3, 3),
        end_date=datetime(2025, 3, 3),
        vacancies=100,
        subscribers=2,
        pendings=1,
        preferences=Preferences(
            accessibility=True, air_conditionating=True, projector=True
        ),
        updated_at=datetime(2024, 2, 24),
        full_allocated=None,
        ignore_to_allocate=None,
    )

    portuguese_schedule = Schedule(
        all_day=None,
        allocated=None,
        end_date=datetime(2025, 2, 2),
        end_time="22:00",
        recurrence=Recurrence.MONTHLY,
        skip_exceptions=None,
        start_date=datetime(2024, 2, 2),
        start_time="10:00",
        university_class=portuguese_class,  # type: ignore
        week_day=WeekDay.MONDAY,
    )

    await portuguese_subject.create()
    await portuguese_class.create()
    await portuguese_schedule.create()


if __name__ == "__main__":
    asyncio.run(create_subject())
