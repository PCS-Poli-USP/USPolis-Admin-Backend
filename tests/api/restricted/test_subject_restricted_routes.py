from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.utils.must_be_int import must_be_int
from tests.factories.model.subject_model_factory import SubjectModelFactory
from tests.factories.request.subject_request_factory import SubjectRequestFactory

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


def test_get_subject_by_id_with_public_client(
    building: Building, session: Session, public_client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    created = factory.create_and_refresh()

    response = public_client.get(f"{URL_PREFIX}/{created.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_subject_with_admin_user(building: Building, client: TestClient) -> None:
    factory = SubjectRequestFactory(building_ids=[must_be_int(building.id)])
    input = factory.create_input()
    response = client.post(URL_PREFIX, json=input.model_dump())
    subject = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert subject["name"] == input.name
    assert subject["code"] == input.code


def test_create_subject_with_restricted_user(
    building: Building, restricted_client: TestClient
) -> None:
    factory = SubjectRequestFactory(building_ids=[must_be_int(building.id)])
    input = factory.create_input()
    response = restricted_client.post(URL_PREFIX, json=input.model_dump())
    subject = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert subject["name"] == input.name
    assert subject["code"] == input.code


def test_create_subject_with_common_user(
    building: Building, common_client: TestClient
) -> None:
    factory = SubjectRequestFactory(building_ids=[must_be_int(building.id)])
    input = factory.create_input()
    response = common_client.post(URL_PREFIX, json=input.model_dump())

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_subject_with_public_client(
    building: Building, session: Session, public_client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    created = factory.create_and_refresh()

    response = public_client.get(f"{URL_PREFIX}/{created.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_subject_with_admin_user(
    building: Building, session: Session, client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    subject = factory.create_and_refresh()

    request_factory = SubjectRequestFactory(building_ids=[must_be_int(building.id)])
    input = request_factory.update_input()

    response = client.put(f"{URL_PREFIX}/{subject.id}", json=input.model_dump())
    updated = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert updated["name"] == input.name
    assert updated["code"] == input.code


def test_update_subject_with_restricted_user(
    building: Building, session: Session, restricted_client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    subject = factory.create_and_refresh()

    request_factory = SubjectRequestFactory(building_ids=[must_be_int(building.id)])
    input = request_factory.update_input()

    response = restricted_client.put(
        f"{URL_PREFIX}/{subject.id}", json=input.model_dump()
    )
    updated = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert updated["name"] == input.name
    assert updated["code"] == input.code


def test_update_subject_with_common_user(
    building: Building, session: Session, common_client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    subject = factory.create_and_refresh()

    request_factory = SubjectRequestFactory(building_ids=[must_be_int(building.id)])
    input = request_factory.update_input()

    response = common_client.put(f"{URL_PREFIX}/{subject.id}", json=input.model_dump())

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_subject_with_admin_user(
    building: Building, session: Session, client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    subject = factory.create_and_refresh()

    response = client.delete(f"{URL_PREFIX}/{subject.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get(f"{URL_PREFIX}/{subject.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_subject_with_restricted_user(
    building: Building, session: Session, restricted_client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    subject = factory.create_and_refresh()

    response = restricted_client.delete(f"{URL_PREFIX}/{subject.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = restricted_client.get(f"{URL_PREFIX}/{subject.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_subject_with_common_user(
    building: Building, session: Session, common_client: TestClient
) -> None:
    factory = SubjectModelFactory(building=building, session=session)
    subject = factory.create_and_refresh()

    response = common_client.delete(
        f"{URL_PREFIX}/{subject.id}",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
