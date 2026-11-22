from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from sqlmodel import Session, select

from server.models.database.mobile_comments_db_model import Comment
from server.models.database.mobile_user_db_model import MobileUser
from tests.utils.mobile_user_test_utils import (
    APP_TOKEN_HEADER,
    make_mobile_user,
    signed_in_as,
)

URL_PREFIX = "/mobile/comments"

_GMAIL_LOGIN_PATCH = "server.routes.public.mobile_comments_routes.gmail_login"
_GMAIL_SEND_PATCH = "server.routes.public.mobile_comments_routes.gmail_send_message"


class TestPostComment:
    """The "Fale conosco" of the app: sent by the app user of the token."""

    @staticmethod
    def _post(
        client: TestClient, user: MobileUser, body: dict[str, object]
    ) -> tuple[Response, MagicMock]:
        with (
            signed_in_as(user),
            patch(_GMAIL_LOGIN_PATCH, return_value=MagicMock()),
            patch(_GMAIL_SEND_PATCH, return_value={"id": "abc"}) as mock_send,
        ):
            response = client.post(URL_PREFIX, json=body, headers=APP_TOKEN_HEADER)
        return response, mock_send

    def test_creates_a_comment_of_the_token_user(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)

        response, mock_send = self._post(
            public_client, user, {"comment": "Great app!", "email": "me@example.com"}
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["comment"] == "Great app!"
        assert body["email"] == "me@example.com"
        comment = session.exec(
            select(Comment).where(Comment.comment == "Great app!")
        ).one()
        assert comment.created_by_id == user.id
        mock_send.assert_called_once()

    def test_accepts_its_own_created_by(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)

        response, _ = self._post(
            public_client, user, {"comment": "Nice feature", "created_by": user.id}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_cannot_comment_as_another_user(
        self, public_client: TestClient, session: Session
    ) -> None:
        me = make_mobile_user(sub="me", session=session)
        other = make_mobile_user(sub="other", session=session)

        response, mock_send = self._post(
            public_client, me, {"comment": "x", "created_by": other.id}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        mock_send.assert_not_called()

    def test_needs_the_app_token(self, public_client: TestClient) -> None:
        with patch(_GMAIL_SEND_PATCH) as mock_send:
            response = public_client.post(URL_PREFIX, json={"comment": "x"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        mock_send.assert_not_called()

    def test_sends_an_email_for_every_comment(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)

        for comment in ("first", "second"):
            _, mock_send = self._post(public_client, user, {"comment": comment})
            mock_send.assert_called_once()


class TestGetAllComments:
    def test_returns_all_comments_to_an_admin(
        self, client: TestClient, session: Session
    ) -> None:
        comment = Comment(comment="hello there", email="a@b.com")
        session.add(comment)
        session.commit()

        response = client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        contents = [c["comment"] for c in response.json()]
        assert "hello there" in contents

    def test_requires_login(self, public_client: TestClient) -> None:
        assert public_client.get(URL_PREFIX).status_code == 401

    def test_refused_to_a_user_who_is_not_admin(
        self, restricted_client: TestClient
    ) -> None:
        assert restricted_client.get(URL_PREFIX).status_code == 403
