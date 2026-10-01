from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.repositories.classroom_permission_repository import (
    ClassroomPermissionRepository,
)
from server.utils.enums.resources_enums import Resource
from tests.factories.request.permission_request_factory import (
    PermissionRequestFactory,
)

URL_PREFIX = "/admin/permissions"


def test_create_permission_with_admin_user(role: Role, client: TestClient) -> None:
    """A permission can no longer target a admin_user directly: role_id is mandatory."""
    input = PermissionRequestFactory(
        role=role, resource=Resource.CLASSROOM
    ).create_input()
    response = client.post(URL_PREFIX, json=input.model_dump())

    assert response.status_code == status.HTTP_201_CREATED


def test_create_permission_without_role_id_is_rejected(
    role: Role, client: TestClient
) -> None:
    """A permission can no longer target a admin_user directly: role_id is mandatory."""
    input = PermissionRequestFactory(
        role=role, resource=Resource.CLASSROOM
    ).create_input()
    payload = input.model_dump()
    del payload["role_id"]

    response = client.post(URL_PREFIX, json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_permission_with_restricted_user(
    role: Role, restricted_client: TestClient
) -> None:
    input = PermissionRequestFactory(
        role=role, resource=Resource.CLASSROOM
    ).create_input()
    response = restricted_client.post(URL_PREFIX, json=input.model_dump())

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_permissions_by_resource(
    role: Role, session: Session, client: TestClient
) -> None:
    input = PermissionRequestFactory(
        role=role, resource=Resource.CLASSROOM
    ).create_input()
    response = client.post(URL_PREFIX, json=input.model_dump())
    assert response.status_code == status.HTTP_201_CREATED

    response = client.get(URL_PREFIX, params={"resource": Resource.CLASSROOM.value})
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["role_id"] == role.id
    assert "user_id" not in data[0]


def test_get_permission_by_id(
    role: Role, admin_user: User, session: Session, client: TestClient
) -> None:
    input = PermissionRequestFactory(
        role=role, resource=Resource.CLASSROOM
    ).create_input()
    created = ClassroomPermissionRepository.create(
        input=input, user=admin_user, session=session
    )
    session.commit()
    session.refresh(created)

    response = client.get(
        f"{URL_PREFIX}/{created.id}", params={"resource": Resource.CLASSROOM.value}
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == created.id
    assert data["role_id"] == role.id


def test_update_permission(role: Role, session: Session, client: TestClient) -> None:
    factory = PermissionRequestFactory(role=role, resource=Resource.CLASSROOM)
    create_input = factory.create_input()
    response = client.post(URL_PREFIX, json=create_input.model_dump())
    permission_id = response.json()["id"]

    update_input = factory.update_input(resource_id=-1)
    response = client.put(
        f"{URL_PREFIX}/{permission_id}", json=update_input.model_dump()
    )

    assert response.status_code == status.HTTP_200_OK


def test_delete_permission(role: Role, client: TestClient) -> None:
    input = PermissionRequestFactory(
        role=role, resource=Resource.CLASSROOM
    ).create_input()
    response = client.post(URL_PREFIX, json=input.model_dump())
    permission_id = response.json()["id"]

    response = client.delete(
        f"{URL_PREFIX}/{permission_id}",
        params={"resource": Resource.CLASSROOM.value},
    )
    assert response.status_code == status.HTTP_200_OK

    response = client.get(
        f"{URL_PREFIX}/{permission_id}", params={"resource": Resource.CLASSROOM.value}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_permissions_batch(role: Role, client: TestClient) -> None:
    factory = PermissionRequestFactory(role=role, resource=Resource.CLASSROOM)
    classroom_input = factory.create_input()
    course_input = PermissionRequestFactory(
        role=role, resource=Resource.COURSE
    ).create_input()

    response = client.post(
        f"{URL_PREFIX}/batch",
        json={
            "permissions": [
                classroom_input.model_dump(),
                course_input.model_dump(),
            ]
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.json()["ids"]) == 2
