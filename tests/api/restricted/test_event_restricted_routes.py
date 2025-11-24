from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from server.models.database.event_db_model import Event
from server.models.database.classroom_db_model import Classroom
from tests.factories.request.event_request_factory import EventRequestFactory
from tests.utils.validators.event.event_model_validator import EventModelAsserts

URL_PREFIX = "/reservations/events"


def test_create_event_with_admin_user(
    classroom: Classroom, client: TestClient, session: Session
) -> None:
    request_factory = EventRequestFactory(classroom=classroom)
    input = request_factory.create_input()
    body = jsonable_encoder(input)

    response = client.post(f"{URL_PREFIX}", json=body)

    assert response.status_code == status.HTTP_201_CREATED

    events = list(session.exec(select(Event)).all())
    assert len(events) == 1

    event = events[0]
    EventModelAsserts.assert_event_after_create(event, input)


def test_create_event_with_restricted_user(
    classroom: Classroom,
    restricted_client: TestClient,
    session: Session,
) -> None:
    request_factory = EventRequestFactory(classroom=classroom)
    input = request_factory.create_input()
    body = jsonable_encoder(input)

    response = restricted_client.post(f"{URL_PREFIX}", json=body)

    assert response.status_code == status.HTTP_201_CREATED

    events = list(session.exec(select(Event)).all())
    assert len(events) == 1

    event = events[0]
    EventModelAsserts.assert_event_after_create(event, input)


def test_create_event_with_common_user(common_client: TestClient) -> None:
    response = common_client.post(f"{URL_PREFIX}", json={})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_event_with_public_user(public_client: TestClient) -> None:
    response = public_client.post(f"{URL_PREFIX}", json={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_event_with_admin_user(
    event: Event,
    classroom: Classroom,
    client: TestClient,
    session: Session,
) -> None:
    request_factory = EventRequestFactory(classroom=classroom)
    input = request_factory.update_input()
    body = jsonable_encoder(input)

    response = client.put(f"{URL_PREFIX}/{event.id}", json=body)

    assert response.status_code == status.HTTP_200_OK

    events = list(session.exec(select(Event)).all())
    assert len(events) == 1

    event = events[0]
    EventModelAsserts.assert_event_after_update(event, input)


def test_update_event_with_restricted_user(
    event: Event,
    classroom: Classroom,
    restricted_client: TestClient,
    session: Session,
) -> None:
    request_factory = EventRequestFactory(classroom=classroom)
    input = request_factory.update_input()
    body = jsonable_encoder(input)

    response = restricted_client.put(f"{URL_PREFIX}/{event.id}", json=body)

    assert response.status_code == status.HTTP_200_OK

    events = list(session.exec(select(Event)).all())
    assert len(events) == 1

    event = events[0]
    EventModelAsserts.assert_event_after_update(event, input)


def test_update_event_with_common_user(common_client: TestClient) -> None:
    response = common_client.put(f"{URL_PREFIX}/1", json={})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_event_with_public_user(public_client: TestClient) -> None:
    response = public_client.put(f"{URL_PREFIX}/1", json={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
