from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from sqlmodel import Session

from server.models.database.institutional_event_db_model import InstitutionalEvent
from server.models.database.mobile_user_db_model import MobileUser
from server.utils.must_be_int import must_be_int
from tests.factories.model.institutional_event_model_factory import (
    InstitutionalEventModelFactory,
)
from tests.utils.mobile_user_test_utils import (
    APP_TOKEN_HEADER,
    make_mobile_user,
    signed_in_as,
)

URL_PREFIX = "/mobile/institutional-events"


def make_event(*, session: Session, likes: int = 0) -> InstitutionalEvent:
    return InstitutionalEventModelFactory(session=session).create_and_refresh(
        likes=likes
    )


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
    """Likes are given by the app user of the token."""

    @staticmethod
    def _like(
        client: TestClient, user: MobileUser, event_id: int, like: bool
    ) -> Response:
        with signed_in_as(user):
            response: Response = client.patch(
                URL_PREFIX,
                json={"event_id": event_id, "user_id": user.id, "like": like},
                headers=APP_TOKEN_HEADER,
            )
        return response

    def test_liking_increments_likes(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)
        event = make_event(session=session, likes=0)

        response = self._like(public_client, user, must_be_int(event.id), True)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["likes"] == 1

    def test_disliking_decrements_likes(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)
        event = make_event(session=session, likes=3)

        response = self._like(public_client, user, must_be_int(event.id), False)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["likes"] == 2

    def test_disliking_never_goes_below_zero(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)
        event = make_event(session=session, likes=0)

        response = self._like(public_client, user, must_be_int(event.id), False)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["likes"] == 0

    def test_returns_404_for_an_unknown_event(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)

        response = self._like(public_client, user, 999999, True)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_like_persists_across_requests(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)
        event = make_event(session=session, likes=0)

        self._like(public_client, user, must_be_int(event.id), True)
        response = self._like(public_client, user, must_be_int(event.id), True)

        assert response.json()["likes"] == 2

    def test_needs_the_app_token(
        self, public_client: TestClient, session: Session
    ) -> None:
        event = make_event(session=session, likes=0)

        response = public_client.patch(
            URL_PREFIX, json={"event_id": event.id, "user_id": 1, "like": True}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_like_as_another_user(
        self, public_client: TestClient, session: Session
    ) -> None:
        me = make_mobile_user(sub="me", session=session)
        other = make_mobile_user(sub="other", session=session)
        event = make_event(session=session, likes=0)

        with signed_in_as(me):
            response = public_client.patch(
                URL_PREFIX,
                json={"event_id": event.id, "user_id": other.id, "like": True},
                headers=APP_TOKEN_HEADER,
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN
