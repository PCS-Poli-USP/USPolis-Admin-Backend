import pytest
from httpx import AsyncClient
from fastapi import status

from tests.utils.subject_test_utils import add_subject, make_subject_register_input
from tests.utils.user_test_utils import add_admin_user
from tests.utils.enums.test_subject_enum import SubjectDefaultValues

from server.models.database.subject_db_model import Subject


MAX_SUBJECT_COUNT = 5
UPDATED_SUBJECT_CODE = "DEF000U"


@pytest.mark.asyncio
async def test_subject_get_all(client: AsyncClient):
    for i in range(MAX_SUBJECT_COUNT):
        await add_subject(f"DEF000{i}")

    response = await client.get("/subjects")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == MAX_SUBJECT_COUNT


@pytest.mark.asyncio
async def test_subject_get(client: AsyncClient):
    subject_id = await add_subject(SubjectDefaultValues.CODE)
    response = await client.get(f"/subjects/{subject_id}")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_subject_create(client: AsyncClient):
    register = make_subject_register_input()
    register.activation = register.activation.isoformat()
    subject_input = dict(register)

    response = await client.post("/subjects", json=subject_input)
    assert response.status_code == status.HTTP_200_OK

    subject_id = response.json()
    assert isinstance(subject_id, str)

    subject = await Subject.by_id(subject_id)
    assert subject.code == register.code


@pytest.mark.asyncio
async def test_subject_update(client: AsyncClient):
    register = make_subject_register_input()
    subject_id = await add_subject(register.code)

    register.code = UPDATED_SUBJECT_CODE
    register.activation = register.activation.isoformat()
    subject_input = dict(register)

    response = await client.patch(f"/subjects/{subject_id}", json=subject_input)
    assert response.status_code == status.HTTP_200_OK

    updated_id = response.json()
    assert isinstance(updated_id, str)

    subject = await Subject.by_id(updated_id)
    assert subject.code == UPDATED_SUBJECT_CODE


@pytest.mark.asyncio
async def test_subject_delete(client: AsyncClient):
    subject_id = await add_subject(SubjectDefaultValues.CODE)

    response = await client.delete(f"/subjects/{subject_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, int)

    assert not await Subject.check_code_exists(SubjectDefaultValues.CODE) 
