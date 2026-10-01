from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from server.models.database.forum_db_model import ForumPost
from server.models.database.mobile_user_db_model import MobileUser
from server.models.database.subject_db_model import Subject
from tests.utils.mobile_user_test_utils import make_mobile_user

URL_PREFIX = "/mobile/forum"

_AUTH_PATCH_TARGET = "server.deps.google_auth_dep.authenticate_with_google"


@pytest.fixture(autouse=True)
def _mock_google_auth() -> Generator[None, None, None]:
    with patch(_AUTH_PATCH_TARGET, return_value={"sub": "irrelevant"}):
        yield


def make_forum_post(
    *,
    subject: Subject,
    user: MobileUser,
    session: Session,
    content: str = "Hello",
    filter_tags: int = 1,
    reply_of_post_id: int | None = None,
    enabled: bool = True,
) -> ForumPost:
    post = ForumPost(
        subject_id=subject.id,
        user_id=user.id,
        content=content,
        filter_tags=filter_tags,
        reply_of_post_id=reply_of_post_id,
        enabled=enabled,
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


class TestGetPosts:
    def test_returns_posts_for_subject_ordered_newest_first(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)
        make_forum_post(subject=subject, user=user, session=session, content="older")
        make_forum_post(subject=subject, user=user, session=session, content="newer")

        response = public_client.get(
            f"{URL_PREFIX}/posts", params={"subject_id": subject.id}
        )

        assert response.status_code == status.HTTP_200_OK
        assert [p["content"] for p in response.json()] == ["newer", "older"]

    def test_excludes_disabled_posts(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)
        make_forum_post(subject=subject, user=user, session=session, content="visible")
        make_forum_post(
            subject=subject,
            user=user,
            session=session,
            content="hidden",
            enabled=False,
        )

        response = public_client.get(
            f"{URL_PREFIX}/posts", params={"subject_id": subject.id}
        )

        contents = [p["content"] for p in response.json()]
        assert contents == ["visible"]

    def test_excludes_replies(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)
        post = make_forum_post(subject=subject, user=user, session=session, content="root")
        make_forum_post(
            subject=subject,
            user=user,
            session=session,
            content="a reply",
            reply_of_post_id=post.id,
        )

        response = public_client.get(
            f"{URL_PREFIX}/posts", params={"subject_id": subject.id}
        )

        assert [p["content"] for p in response.json()] == ["root"]

    def test_filters_by_search_keyword(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)
        make_forum_post(
            subject=subject, user=user, session=session, content="about python"
        )
        make_forum_post(subject=subject, user=user, session=session, content="about java")

        response = public_client.get(
            f"{URL_PREFIX}/posts",
            params={"subject_id": subject.id, "search_keyword": "python"},
        )

        assert [p["content"] for p in response.json()] == ["about python"]

    def test_filters_by_prime_tags(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)
        make_forum_post(subject=subject, user=user, session=session, content="tag2", filter_tags=2)
        make_forum_post(subject=subject, user=user, session=session, content="tag3", filter_tags=3)
        make_forum_post(
            subject=subject, user=user, session=session, content="tag6", filter_tags=6
        )

        response = public_client.get(
            f"{URL_PREFIX}/posts",
            params={"subject_id": subject.id, "filter_tags": [2]},
        )

        contents = {p["content"] for p in response.json()}
        assert contents == {"tag2", "tag6"}


class TestCreateForumPost:
    def test_creates_a_post_for_a_normal_subject(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)

        response = public_client.post(
            f"{URL_PREFIX}/posts",
            json={"user_id": user.id, "content": "hello", "subject_id": subject.id},
            headers={"authorization": "Bearer whatever"},
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["content"] == "hello"
        assert body["subject_id"] == subject.id
        assert body["user_name"] == f"{user.given_name} {user.family_name}"

    def test_creates_general_forum_subject_when_missing(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)

        response = public_client.post(
            f"{URL_PREFIX}/posts",
            json={"user_id": user.id, "content": "general", "subject_id": -1},
            headers={"authorization": "x"},
        )

        assert response.status_code == status.HTTP_200_OK
        general_subject = session.exec(
            select(Subject).where(Subject.name == "Forum Geral")
        ).one()
        assert response.json()["subject_id"] == general_subject.id

    def test_reuses_existing_general_forum_subject(
        self, public_client: TestClient, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)

        public_client.post(
            f"{URL_PREFIX}/posts",
            json={"user_id": user.id, "content": "first", "subject_id": -1},
            headers={"authorization": "x"},
        )
        public_client.post(
            f"{URL_PREFIX}/posts",
            json={"user_id": user.id, "content": "second", "subject_id": -1},
            headers={"authorization": "x"},
        )

        general_subjects = session.exec(
            select(Subject).where(Subject.name == "Forum Geral")
        ).all()
        assert len(general_subjects) == 1


class TestDeleteForumPost:
    def test_disables_the_post(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)
        post = make_forum_post(subject=subject, user=user, session=session)

        response = public_client.delete(
            f"{URL_PREFIX}/posts/{post.id}", headers={"authorization": "x"}
        )

        assert response.status_code == status.HTTP_200_OK
        session.refresh(post)
        assert post.enabled is False


class TestReportForumPost:
    def test_increments_report_count_once_per_user(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        author = make_mobile_user(sub="author", session=session)
        reporter = make_mobile_user(sub="reporter", session=session)
        post = make_forum_post(subject=subject, user=author, session=session)

        response = public_client.post(
            f"{URL_PREFIX}/report", json={"post_id": post.id, "user_id": reporter.id}
        )
        assert response.json()["report_count"] == 1

        # Same user reporting again must not double-count.
        response = public_client.post(
            f"{URL_PREFIX}/report", json={"post_id": post.id, "user_id": reporter.id}
        )
        assert response.json()["report_count"] == 1

    def test_sends_email_when_report_count_reaches_ten(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        author = make_mobile_user(sub="author", session=session)
        post = make_forum_post(subject=subject, user=author, session=session)
        reporters = [
            make_mobile_user(sub=f"reporter{i}", session=session) for i in range(10)
        ]

        with (
            patch(
                "server.routes.public.forum_routes.gmail_login",
                return_value=MagicMock(),
            ) as mock_login,
            patch(
                "server.routes.public.forum_routes.gmail_send_message",
                return_value={"id": "abc"},
            ) as mock_send,
        ):
            for reporter in reporters:
                response = public_client.post(
                    f"{URL_PREFIX}/report",
                    json={"post_id": post.id, "user_id": reporter.id},
                )

        assert response.json()["report_count"] == 10
        mock_login.assert_called_once()
        mock_send.assert_called_once()


class TestCreateForumPostReply:
    def test_creates_a_reply_and_increments_parent_replies_count(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        author = make_mobile_user(sub="author", session=session)
        post = make_forum_post(subject=subject, user=author, session=session)
        replier = make_mobile_user(sub="replier", session=session)

        response = public_client.post(
            f"{URL_PREFIX}/posts/{post.id}",
            json={"user_id": replier.id, "content": "a reply", "subject_id": subject.id},
            headers={"authorization": "x"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["reply_of_post_id"] == post.id
        session.refresh(post)
        assert post.replies_count == 1

    def test_returns_404_when_parent_post_does_not_exist(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        replier = make_mobile_user(sub="replier", session=session)

        response = public_client.post(
            f"{URL_PREFIX}/posts/999999",
            json={"user_id": replier.id, "content": "a reply", "subject_id": subject.id},
            headers={"authorization": "x"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetForumPostReplies:
    def test_returns_all_replies_for_a_post_oldest_first(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        author = make_mobile_user(sub="author", session=session)
        post = make_forum_post(subject=subject, user=author, session=session)
        make_forum_post(
            subject=subject,
            user=author,
            session=session,
            content="reply1",
            reply_of_post_id=post.id,
        )
        make_forum_post(
            subject=subject,
            user=author,
            session=session,
            content="reply2",
            reply_of_post_id=post.id,
        )

        response = public_client.get(
            f"{URL_PREFIX}/posts/{post.id}", params={"user_id": author.id}
        )

        assert response.status_code == status.HTTP_200_OK
        assert [r["content"] for r in response.json()] == ["reply1", "reply2"]


class TestUpdateForumPostLike:
    def test_likes_a_post(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        author = make_mobile_user(sub="author", session=session)
        liker = make_mobile_user(sub="liker", session=session)
        post = make_forum_post(subject=subject, user=author, session=session)

        response = public_client.post(
            f"{URL_PREFIX}/posts/{post.id}/liked",
            json={"post_id": post.id, "user_id": liker.id, "like_state": True},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["likes_count"] == 1

    def test_unlikes_a_post(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        author = make_mobile_user(sub="author", session=session)
        liker = make_mobile_user(sub="liker", session=session)
        post = make_forum_post(subject=subject, user=author, session=session)

        public_client.post(
            f"{URL_PREFIX}/posts/{post.id}/liked",
            json={"post_id": post.id, "user_id": liker.id, "like_state": True},
        )
        response = public_client.post(
            f"{URL_PREFIX}/posts/{post.id}/liked",
            json={"post_id": post.id, "user_id": liker.id, "like_state": False},
        )

        assert response.json()["likes_count"] == 0


class TestAuthenticationGate:
    def test_create_post_returns_401_for_an_invalid_token(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        user = make_mobile_user(sub="u1", session=session)

        with patch(_AUTH_PATCH_TARGET, side_effect=ValueError("Wrong number of segments")):
            response = public_client.post(
                f"{URL_PREFIX}/posts",
                json={"user_id": user.id, "content": "x", "subject_id": subject.id},
                headers={"authorization": "bad-token"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_post_returns_401_for_an_invalid_token(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        author = make_mobile_user(sub="author", session=session)
        post = make_forum_post(subject=subject, user=author, session=session)

        with patch(_AUTH_PATCH_TARGET, side_effect=ValueError("Wrong number of segments")):
            response = public_client.delete(
                f"{URL_PREFIX}/posts/{post.id}", headers={"authorization": "bad-token"}
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_reply_returns_401_for_an_invalid_token(
        self, public_client: TestClient, subject: Subject, session: Session
    ) -> None:
        author = make_mobile_user(sub="author", session=session)
        post = make_forum_post(subject=subject, user=author, session=session)
        replier = make_mobile_user(sub="replier", session=session)

        with patch(_AUTH_PATCH_TARGET, side_effect=ValueError("Wrong number of segments")):
            response = public_client.post(
                f"{URL_PREFIX}/posts/{post.id}",
                json={
                    "user_id": replier.id,
                    "content": "a reply",
                    "subject_id": subject.id,
                },
                headers={"authorization": "bad-token"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
