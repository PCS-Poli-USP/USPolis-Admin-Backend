from fastapi import status
from fastapi.testclient import TestClient


from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from tests.utils.validators.classroom.classroom_response_validator import (
    assert_get_classroom_full_response_list,
    assert_get_classroom_response_list,
)

URL_PREFIX = "/classrooms"


def test_get_all_classrooms_with_admin_user(
    client: TestClient,
    classrooms: list[Classroom],
) -> None:
    response = client.get(URL_PREFIX)
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_response_list(response, classrooms)


def test_get_all_classrooms_with_restricted_user(
    restricted_client: TestClient,
    classrooms: list[Classroom],
) -> None:
    response = restricted_client.get(URL_PREFIX)
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_response_list(response, classrooms)


def test_get_all_classrooms_with_common_user(
    common_client: TestClient,
    classrooms: list[Classroom],
) -> None:
    response = common_client.get(URL_PREFIX)
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_response_list(response, classrooms)


def test_get_all_classrooms_with_public_user(
    public_client: TestClient,
    classrooms: list[Classroom],
) -> None:
    response = public_client.get(URL_PREFIX)
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_response_list(response, classrooms)


def test_get_all_classrooms_full_with_admin_user(
    client: TestClient,
    allocated_classrooms: tuple[list[Classroom], list[Class]],
) -> None:
    classrooms, classes = allocated_classrooms
    response = client.get(f"{URL_PREFIX}/full/")
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_full_response_list(response, classrooms, classes)


def test_get_all_classrooms_full_with_restricted_user(
    restricted_client: TestClient,
    allocated_classrooms: tuple[list[Classroom], list[Class]],
) -> None:
    classrooms, classes = allocated_classrooms
    response = restricted_client.get(f"{URL_PREFIX}/full/")
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_full_response_list(response, classrooms, classes)


def test_get_all_classrooms_full_with_common_user(
    common_client: TestClient,
    allocated_classrooms: tuple[list[Classroom], list[Class]],
) -> None:
    classrooms, classes = allocated_classrooms
    response = common_client.get(f"{URL_PREFIX}/full/")
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_full_response_list(response, classrooms, classes)


def test_get_all_classrooms_with_full_public_user(
    public_client: TestClient,
    allocated_classrooms: tuple[list[Classroom], list[Class]],
) -> None:
    classrooms, classes = allocated_classrooms
    response = public_client.get(f"{URL_PREFIX}/full/")
    assert response.status_code == status.HTTP_200_OK
    assert_get_classroom_full_response_list(response, classrooms, classes)
