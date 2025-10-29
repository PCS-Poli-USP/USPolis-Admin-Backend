from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from server.models.database.classroom_db_model import Classroom
from server.models.database.meeting_db_model import Meeting
from tests.factories.request.meeting_request_factory import MeetingRequestFactory
from tests.utils.validators.meeting.meeting_model_validator import MeetingModelAsserts

URL_PREFIX = "/reservations/meetings"


def test_create_meeting_with_admin_user(
    classroom: Classroom, client: TestClient, session: Session
) -> None:
    request_factory = MeetingRequestFactory(classroom)
    input = request_factory.create_input()
    body = jsonable_encoder(input)

    response = client.post(f"{URL_PREFIX}", json=body)

    assert response.status_code == status.HTTP_201_CREATED

    meetings = list(session.exec(select(Meeting)).all())
    assert len(meetings) == 1

    meeting = meetings[0]
    MeetingModelAsserts.assert_meeting_after_create(meeting, input)


def test_create_meeting_with_restricted_user(
    classroom: Classroom, restricted_client: TestClient, session: Session
) -> None:
    request_factory = MeetingRequestFactory(classroom)
    input = request_factory.create_input()
    body = jsonable_encoder(input)

    response = restricted_client.post(f"{URL_PREFIX}", json=body)

    assert response.status_code == status.HTTP_201_CREATED

    meetings = list(session.exec(select(Meeting)).all())
    assert len(meetings) == 1

    meeting = meetings[0]
    MeetingModelAsserts.assert_meeting_after_create(meeting, input)


def test_create_meeting_with_common_user(
    classroom: Classroom, common_client: TestClient
) -> None:
    request_factory = MeetingRequestFactory(classroom)
    input = request_factory.create_input()
    body = jsonable_encoder(input)

    response = common_client.post(f"{URL_PREFIX}", json=body)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_meeting_with_public_user(
    classroom: Classroom, public_client: TestClient
) -> None:
    request_factory = MeetingRequestFactory(classroom)
    input = request_factory.create_input()
    body = jsonable_encoder(input)

    response = public_client.post(f"{URL_PREFIX}", json=body)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_meeting_with_admin_user(
    meeting: Meeting, classroom: Classroom, client: TestClient, session: Session
) -> None:
    request_factory = MeetingRequestFactory(classroom)
    input = request_factory.update_input()
    body = jsonable_encoder(input)

    response = client.put(f"{URL_PREFIX}/{meeting.id}", json=body)

    assert response.status_code == status.HTTP_200_OK

    meetings = list(session.exec(select(Meeting)).all())
    assert len(meetings) == 1

    meeting = meetings[0]
    MeetingModelAsserts.assert_meeting_after_update(meeting, input)


def test_update_meeting_with_restricted_user(
    meeting: Meeting,
    classroom: Classroom,
    restricted_client: TestClient,
    session: Session,
) -> None:
    request_factory = MeetingRequestFactory(classroom)
    input = request_factory.update_input()
    body = jsonable_encoder(input)

    response = restricted_client.put(f"{URL_PREFIX}", json=body)

    assert response.status_code == status.HTTP_201_CREATED

    meetings = list(session.exec(select(Meeting)).all())
    assert len(meetings) == 1

    meeting = meetings[0]
    MeetingModelAsserts.assert_meeting_after_update(meeting, input)


def test_update_meeting_with_common_user(
    meeting: Meeting, classroom: Classroom, common_client: TestClient
) -> None:
    request_factory = MeetingRequestFactory(classroom)
    input = request_factory.update_input()
    body = jsonable_encoder(input)

    response = common_client.put(f"{URL_PREFIX}/{meeting.id}", json=body)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_meeting_with_public_user(
    meeting: Meeting, classroom: Classroom, public_client: TestClient
) -> None:
    request_factory = MeetingRequestFactory(classroom)
    input = request_factory.update_input()
    body = jsonable_encoder(input)

    response = public_client.put(f"{URL_PREFIX}/{meeting.id}", json=body)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
