from sqlmodel import Session

from server.models.database.subject_db_model import Subject
from server.models.http.responses.forum_post_response import (
    ForumPostReplyResponse,
    ForumPostResponse,
)
from server.repositories.forum_repository import ForumRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.forum_post_model_factory import ForumPostModelFactory
from tests.utils.mobile_user_test_utils import make_mobile_user


def test_from_forum_post_without_a_like(session: Session, subject: Subject) -> None:
    author = make_mobile_user(sub="author-sub", session=session)
    post = ForumPostModelFactory(
        subject=subject, user=author, session=session
    ).create_and_refresh(content="Alguém tem o gabarito?")

    data = ForumPostResponse.from_forum_post(
        mobile_user_id=None, post=post, session=session
    )

    assert data.id == post.id
    assert data.subject_id == subject.id
    assert data.content == "Alguém tem o gabarito?"
    assert data.user_name == f"{author.given_name} {author.family_name}"
    assert data.user_liked is False


def test_from_forum_post_with_a_like(session: Session, subject: Subject) -> None:
    author = make_mobile_user(sub="author-sub-2", session=session)
    liker = make_mobile_user(sub="liker-sub", session=session)
    post = ForumPostModelFactory(
        subject=subject, user=author, session=session
    ).create_and_refresh()
    ForumRepository.change_forum_post_like(
        post_id=must_be_int(post.id),
        mobile_user_id=must_be_int(liker.id),
        like_state=True,
        session=session,
    )

    data = ForumPostResponse.from_forum_post(
        mobile_user_id=liker.id, post=post, session=session
    )

    assert data.user_liked is True


def test_from_forum_post_list(session: Session, subject: Subject) -> None:
    author = make_mobile_user(sub="author-sub-3", session=session)
    post1 = ForumPostModelFactory(
        subject=subject, user=author, session=session
    ).create_and_refresh()
    post2 = ForumPostModelFactory(
        subject=subject, user=author, session=session
    ).create_and_refresh()

    data = ForumPostResponse.from_forum_post_list(
        mobile_user_id=None, posts=[post1, post2], session=session
    )

    assert [d.id for d in data] == [post1.id, post2.id]


def test_from_forum_reply(session: Session, subject: Subject) -> None:
    author = make_mobile_user(sub="author-sub-4", session=session)
    parent = ForumPostModelFactory(
        subject=subject, user=author, session=session
    ).create_and_refresh()
    reply = ForumPostModelFactory(
        subject=subject, user=author, session=session, reply_of_post_id=parent.id
    ).create_and_refresh(content="Concordo!")

    data = ForumPostReplyResponse.from_forum_reply(
        reply=reply, mobile_user_id=None, session=session
    )

    assert data.id == reply.id
    assert data.reply_of_post_id == parent.id
    assert data.content == "Concordo!"


def test_from_forum_post_reply_list(session: Session, subject: Subject) -> None:
    author = make_mobile_user(sub="author-sub-5", session=session)
    parent = ForumPostModelFactory(
        subject=subject, user=author, session=session
    ).create_and_refresh()
    reply1 = ForumPostModelFactory(
        subject=subject, user=author, session=session, reply_of_post_id=parent.id
    ).create_and_refresh()
    reply2 = ForumPostModelFactory(
        subject=subject, user=author, session=session, reply_of_post_id=parent.id
    ).create_and_refresh()

    data = ForumPostReplyResponse.from_forum_post_reply_list(
        [reply1, reply2], None, session
    )

    assert [d.id for d in data] == [reply1.id, reply2.id]
