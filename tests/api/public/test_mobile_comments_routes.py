from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from server.models.database.mobile_comments_db_model import Comment
from tests.utils.mobile_user_test_utils import make_mobile_user

URL_PREFIX = "/mobile/comments"

_GMAIL_LOGIN_PATCH = "server.routes.public.mobile_comments_routes.gmail_login"
_GMAIL_SEND_PATCH = "server.routes.public.mobile_comments_routes.gmail_send_message"


class TestPostComment:
    def test_creates_a_comment_without_a_user(
        self, public_client: TestClient, session: Session
    ) -> None:
        with (
            patch(_GMAIL_LOGIN_PATCH, return_value=MagicMock()),
            patch(_GMAIL_SEND_PATCH, return_value={"id": "abc"}) as mock_send,
        ):
            response = public_client.post(
                URL_PREFIX,
                json={"comment": "Great app!", "email": "guest@example.com"},
            )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["comment"] == "Great app!"
        assert body["email"] == "guest@example.com"
        mock_send.assert_called_once()

    def test_creates_a_comment_linked_to_a_mobile_user(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)

        with (
            patch(_GMAIL_LOGIN_PATCH, return_value=MagicMock()),
            patch(_GMAIL_SEND_PATCH, return_value={"id": "abc"}),
        ):
            response = public_client.post(
                URL_PREFIX,
                json={"comment": "Nice feature", "created_by": user.id},
            )

        assert response.status_code == status.HTTP_200_OK
        comment = session.exec(
            select(Comment).where(Comment.comment == "Nice feature")
        ).one()
        assert comment.created_by_id == user.id

    def test_returns_404_for_an_unknown_created_by_user(
        self, public_client: TestClient, session: Session
    ) -> None:
        with (
            patch(_GMAIL_LOGIN_PATCH, return_value=MagicMock()),
            patch(_GMAIL_SEND_PATCH, return_value={"id": "abc"}),
        ):
            response = public_client.post(
                URL_PREFIX,
                json={"comment": "x", "created_by": 999999},
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_sends_an_email_for_every_comment(
        self, public_client: TestClient, session: Session
    ) -> None:
        with (
            patch(_GMAIL_LOGIN_PATCH, return_value=MagicMock()) as mock_login,
            patch(_GMAIL_SEND_PATCH, return_value={"id": "abc"}) as mock_send,
        ):
            public_client.post(URL_PREFIX, json={"comment": "first"})
            public_client.post(URL_PREFIX, json={"comment": "second"})

        assert mock_login.call_count == 2
        assert mock_send.call_count == 2


class TestGetAllComments:
    def test_returns_all_comments(
        self, public_client: TestClient, session: Session
    ) -> None:
        comment = Comment(comment="hello there", email="a@b.com")
        session.add(comment)
        session.commit()

        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        contents = [c["comment"] for c in response.json()]
        assert "hello there" in contents
