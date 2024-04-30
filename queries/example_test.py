import asyncio
from datetime import datetime

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