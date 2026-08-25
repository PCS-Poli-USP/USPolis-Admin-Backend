from fastapi import status
from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session

from server.models.database.role_db_model import Role
from server.repositories.role_repository import RoleNotFound, RoleRepository
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int
from tests.factories.request.role_request_factory import RoleRequestFactory

URL_PREFIX = "/admin/roles"


def test_get_roles_with_admin_user(role: Role, client: TestClient) -> None:
    response = client.get(URL_PREFIX)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["id"] == role.id


def test_get_roles_with_restricted_user(role: Role, restricted_client: TestClient) -> None:
    response = restricted_client.get(URL_PREFIX)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_role_by_id_with_admin_user(role: Role, client: TestClient) -> None:
    response = client.get(f"{URL_PREFIX}/{role.id}")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == role.id
    assert data["name"] == role.name
    assert data["permissions"] == []


def test_get_role_by_id_not_found(client: TestClient) -> None:
    response = client.get(f"{URL_PREFIX}/-1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_role_without_permissions(client: TestClient) -> None:
    input = RoleRequestFactory(resources=[]).create_input()
    response = client.post(URL_PREFIX, json=input.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"]


def test_create_role_with_permissions(session: Session, client: TestClient) -> None:
    factory = RoleRequestFactory(resources=[Resource.CLASSROOM])
    input = factory.create_input(
        permissions=[factory.build_permission(Resource.CLASSROOM)]
    )
    response = client.post(URL_PREFIX, json=input.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    role_id = response.json()["id"]

    role = RoleRepository.get_by_id(id=role_id, session=session)
    assert len(role.classroom_permissions) == 1


def test_create_role_with_restricted_user(restricted_client: TestClient) -> None:
    input = RoleRequestFactory(resources=[]).create_input()
    response = restricted_client.post(URL_PREFIX, json=input.model_dump())

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_role(role: Role, session: Session, client: TestClient) -> None:
    factory = RoleRequestFactory(resources=role.resources)
    input = factory.update_input(
        name="Novo nome do cargo",
        description=role.description,
        resources=role.resources,
        permissions=[factory.build_permission(Resource.CLASSROOM)],
    )
    response = client.put(f"{URL_PREFIX}/{role.id}", json=input.model_dump())

    assert response.status_code == status.HTTP_200_OK

    updated = RoleRepository.get_by_id(id=must_be_int(role.id), session=session)
    assert updated.name == "Novo nome do cargo"
    assert len(updated.classroom_permissions) == 1


def test_update_role_with_restricted_user(
    role: Role, restricted_client: TestClient
) -> None:
    input = RoleRequestFactory(resources=role.resources).update_input()
    response = restricted_client.put(f"{URL_PREFIX}/{role.id}", json=input.model_dump())

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_role(role: Role, session: Session, client: TestClient) -> None:
    response = client.delete(f"{URL_PREFIX}/{role.id}")
    assert response.status_code == status.HTTP_200_OK

    with pytest.raises(RoleNotFound):
        RoleRepository.get_by_id(id=must_be_int(role.id), session=session)


def test_delete_role_with_restricted_user(
    role: Role, restricted_client: TestClient
) -> None:
    response = restricted_client.delete(f"{URL_PREFIX}/{role.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
