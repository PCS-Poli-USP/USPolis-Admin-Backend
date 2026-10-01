from datetime import datetime

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.institutional_event_db_model import InstitutionalEvent

URL_PREFIX = "/mobile/institutional-events"


def make_event(*, session: Session, likes: int = 0) -> InstitutionalEvent:
    event = InstitutionalEvent(
        title="Semana da Computação",
        description="Uma semana cheia de palestras",
        category="talk",
        start=datetime(2025, 5, 1, 10, 0),
        end=datetime(2025, 5, 1, 12, 0),
        location="Auditório",
        building="Bloco A",
        classroom="A1",
        external_link=None,
        likes=likes,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


class TestGetAllInstitutionalEvents:
    def test_returns_all_events(
        self, public_client: TestClient, session: Session
    ) -> None:
        event = make_event(session=session)

        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        matches = [e for e in response.json() if e["id"] == event.id]
        assert len(matches) == 1
        assert matches[0]["title"] == event.title
        assert matches[0]["likes"] == 0


class TestHandleInstitutionalEventLike:
    def test_liking_increments_likes(
        self, public_client: TestClient, session: Session
    ) -> None:
        event = make_event(session=session, likes=0)

        response = public_client.patch(
            URL_PREFIX,
            json={"event_id": event.id, "user_id": 1, "like": True},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["likes"] == 1

    def test_disliking_decrements_likes(
        self, public_client: TestClient, session: Session
    ) -> None:
        event = make_event(session=session, likes=3)

        response = public_client.patch(
            URL_PREFIX,
            json={"event_id": event.id, "user_id": 1, "like": False},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["likes"] == 2

    def test_disliking_never_goes_below_zero(
        self, public_client: TestClient, session: Session
    ) -> None:
        event = make_event(session=session, likes=0)

        response = public_client.patch(
            URL_PREFIX,
            json={"event_id": event.id, "user_id": 1, "like": False},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["likes"] == 0

    def test_returns_404_for_an_unknown_event(
        self, public_client: TestClient, session: Session
    ) -> None:
        response = public_client.patch(
            URL_PREFIX,
            json={"event_id": 999999, "user_id": 1, "like": True},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_like_persists_across_requests(
        self, public_client: TestClient, session: Session
    ) -> None:
        event = make_event(session=session, likes=0)

        public_client.patch(
            URL_PREFIX, json={"event_id": event.id, "user_id": 1, "like": True}
        )
        response = public_client.patch(
            URL_PREFIX, json={"event_id": event.id, "user_id": 1, "like": True}
        )

        assert response.json()["likes"] == 2
