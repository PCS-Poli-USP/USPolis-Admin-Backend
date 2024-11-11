from fastapi import status
from fastapi.testclient import TestClient
from json import loads
from sqlmodel import Session

from server.repositories.subject_repository import SubjectRepository
from server.utils.must_be_int import must_be_int
from tests.utils.building_test_utils import add_building, make_building
from tests.utils.default_values.test_building_default_values import (
    BuildingDefaultValues,
)
from tests.utils.subject_test_utils import (
    check_code_exists,
    create_subject,
    make_subject_register_input,
    make_subject_update_input,
)
from tests.utils.default_values.test_subject_default_values import SubjectDefaultValues

from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User

MAX_SUBJECT_COUNT = 5
UPDATED_SUBJECT_CODE = "DEF000U"


def test_subject_get_all(db: Session, client: TestClient, user: User) -> None:
    building = make_building(name=BuildingDefaultValues.NAME, user=user)
    db.add(building)

    subject_ids = []
    for i in range(MAX_SUBJECT_COUNT):
        subject_id = create_subject(
            session=db,
            code=f"DEF000{
                                    i}",
            buildings=[building],
        )
        subject_ids.append(subject_id)

    response = client.get("/subjects")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == MAX_SUBJECT_COUNT

    data_ids = [subject["id"] for subject in data]
    for i in range(len(subject_ids)):
        assert subject_ids[i] in data_ids


def test_subject_get(db: Session, client: TestClient, user: User) -> None:
    building = make_building(name=BuildingDefaultValues.NAME, user=user)
    db.add(building)
    subject_id = create_subject(
        session=db, code=SubjectDefaultValues.CODE, buildings=[building]
    )
    response = client.get(f"/subjects/{subject_id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data is not None
    assert data["name"] == SubjectDefaultValues.NAME
    assert data["code"] == SubjectDefaultValues.CODE
    assert data["professors"] == SubjectDefaultValues.PROFESSORS


def test_subject_create(db: Session, client: TestClient, user: User) -> None:
    building_id = add_building(session=db, name=BuildingDefaultValues.NAME, user=user)
    register = make_subject_register_input(building_ids=[building_id])
    subject_input = register.model_dump_json()

    response = client.post("/subjects", json=loads(subject_input))
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    id = data["id"]
    subject = db.get(Subject, id)
    assert subject is not None

    if subject:
        assert subject.code == register.code
        assert subject.name == register.name
        building_ids = [building.id for building in subject.buildings]
        assert building_id in building_ids


def test_subject_update(db: Session, client: TestClient, user: User) -> None:
    building = make_building(name=BuildingDefaultValues.NAME, user=user)
    db.add(building)
    buildings = [building]

    subject_id = create_subject(
        session=db, code=SubjectDefaultValues.CODE, buildings=buildings
    )
    input = make_subject_update_input(building_ids=[must_be_int(building.id)])

    input.code = UPDATED_SUBJECT_CODE
    subject_input = input.model_dump_json()

    response = client.put(f"/subjects/{subject_id}", json=loads(subject_input))
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data is not None
    assert data["id"] == subject_id

    subject = SubjectRepository.get_by_id(id=subject_id, session=db)
    assert subject.code == UPDATED_SUBJECT_CODE


def test_subject_delete(db: Session, client: TestClient, user: User) -> None:
    building = make_building(name=BuildingDefaultValues.NAME, user=user)
    db.add(building)

    subject_id = create_subject(
        session=db, code=SubjectDefaultValues.CODE, buildings=[building]
    )

    response = client.delete(f"/subjects/{subject_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not check_code_exists(db=db, code=SubjectDefaultValues.CODE)
