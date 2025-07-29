from fastapi import status
from fastapi.testclient import TestClient

from sqlmodel import Session

from server.models.database.user_db_model import User
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.class_db_model import Class

from server.repositories.occurrence_repository import OccurrenceRepository
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.utils.validators.classroom.classroom_response_validator import (
    assert_get_classroom_full_response,
    assert_get_classroom_response,
)


URL_PREFIX = "/classrooms"


def test_get_classroom_by_id_with_admin_user(
    classroom: Classroom, client: TestClient
) -> None:
    response = client.get(f"{URL_PREFIX}/{classroom.id}")

    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_response(response, classroom)


def test_get_classroom_by_id_with_restricted_user(
    classroom: Classroom,
    restricted_client: TestClient,
) -> None:
    response = restricted_client.get(f"{URL_PREFIX}/{classroom.id}")
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_response(response, classroom)


def test_get_classroom_by_id_with_restricted_user_outisder_group(
    restricted_user: User,
    building: Building,
    session: Session,
    restricted_client: TestClient,
) -> None:
    insider_group = GroupModelFactory(
        building=building, session=session
    ).create_and_refresh()

    outsider_group = GroupModelFactory(
        building=building, session=session
    ).create_and_refresh(users=[restricted_user])

    classroom = ClassroomModelFactory(
        creator=restricted_user, building=building, group=insider_group, session=session
    ).create_and_refresh()

    response = restricted_client.get(f"{URL_PREFIX}/{classroom.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert outsider_group.classrooms == []


def test_get_classroom_by_id_with_common_user(
    classroom: Classroom, common_client: TestClient
) -> None:
    response = common_client.get(f"{URL_PREFIX}/{classroom.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_classroom_by_id_with_public_user(
    classroom: Classroom, public_client: TestClient
) -> None:
    response = public_client.get(f"{URL_PREFIX}/{classroom.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_classroom_full_with_admin_user(
    user: User,
    classroom: Classroom,
    class_: Class,
    client: TestClient,
    session: Session,
) -> None:
    OccurrenceRepository.allocate_schedule(
        user=user, classroom=classroom, schedule=class_.schedules[0], session=session
    )
    response = client.get(f"{URL_PREFIX}/full/{classroom.id}")
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_full_response(response, classroom, class_)


def test_get_classroom_full_with_restricted_user(
    allocated_classroom: Classroom,
    class_: Class,
    restricted_client: TestClient,
) -> None:
    response = restricted_client.get(f"{URL_PREFIX}/full/{allocated_classroom.id}")
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_full_response(response, allocated_classroom, class_)


def test_get_classroom_full_with_common_user(
    allocated_classroom: Classroom,
    class_: Class,
    common_client: TestClient,
) -> None:
    response = common_client.get(f"{URL_PREFIX}/full/{allocated_classroom.id}")
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_full_response(response, allocated_classroom, class_)


def test_get_classroom_full_with_public_user(
    classroom: Classroom, public_client: TestClient
) -> None:
    response = public_client.get(f"{URL_PREFIX}/full/{classroom.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
