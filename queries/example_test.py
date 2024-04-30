from database.mongo import Database
from database.models.user_building import Building, User
from database.models.subject import Subject

import asyncio
import sys
import os
from datetime import datetime

current_directory = os.getcwd()
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
sys.path.append(parent_directory)


async def example():
    client = await Database.get_client()

    user = User(
        cognito_id='COGNITO_ID_SAMPLE',
        username='usernameTest',
        name='Nome de Teste',
        email='Email@test.br',
        is_admin=True,
        updated_at=datetime.now())

    building_test = Building(name='Prédio Teste', created_by=user,
                             updated_at=datetime.now())

    portuguese = Subject(
        subject_code="Teste",
        buildings=[building_test],
        name="Portugues",
        professors=["Eu"],
        type="pratica",
        class_credit=2,
        work_credit=5,
        activation=datetime(2024, 2, 2),
        desactivation=datetime(2025, 2, 2),
    )

    await user.create()
    await building_test.create()
    await portuguese.create()

if __name__ == "__main__":
    asyncio.run(example())
