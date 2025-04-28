from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.building_db_model import Building
from tests.factories.model.subject_model_factory import SubjectModelFactory

URL_PREFIX = "/subjects"


def test_get_subject_by_id_with_admin_user(
    building: Building, session: Session, client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    created = factory.create_and_refresh()

    response = client.get(f"{URL_PREFIX}/{created.id}")
    subject = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert subject["id"] == created.id
    assert subject["code"] == created.code
    assert subject["name"] == created.name
    assert subject["type"] == created.type.value


def test_get_subject_by_id_with_restricted_user(
    building: Building, session: Session, restricted_client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    created = factory.create_and_refresh()

    response = restricted_client.get(f"{URL_PREFIX}/{created.id}")
    subject = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert subject["id"] == created.id
    assert subject["code"] == created.code
    assert subject["name"] == created.name
    assert subject["type"] == created.type.value


def test_get_subject_by_id_with_common_user(
    building: Building, session: Session, common_client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    created = factory.create_and_refresh()

    response = common_client.get(f"{URL_PREFIX}/{created.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN
