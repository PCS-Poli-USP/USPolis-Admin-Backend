import asyncio
import sys
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import Document, Indexed, init_beanie

current_directory = os.getcwd()
print(current_directory)
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
print(parent_directory)
sys.path.append(parent_directory)

from database.models.subject import Subject
from database.mongo import Database

async def example():
    client = await Database.get_client()

    portuguese = Subject(
        subject_code="Teste",
        name="Portugues",
        professors=["Eu"],
        type="pratica",
        class_credit=2,
        work_credit=5,
        activation=datetime(2024, 2, 2),
        desactivation=datetime(2025, 2, 2),
    )

    await portuguese.create()

if __name__ == "__main__":
    asyncio.run(example())