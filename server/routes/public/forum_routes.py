from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query, status

from server.deps.google_auth_dep import MobileUserDep, check_acting_as
from server.deps.session_dep import SessionDep
from server.models.database.forum_db_model import ForumPost
from server.models.database.subject_db_model import Subject
from server.models.http.requests.email_request_models import ForumPostReportedMail
from server.models.http.requests.forum_request_models import (
    ForumPostLike,
    ForumPostRegister,
    ForumReportRegister,
    to_forumpost_model,
    to_forumreply_model,
)
from server.models.http.responses.forum_post_response import (
    ForumPostReplyResponse,
    ForumPostResponse,
)
from server.repositories.forum_repository import ForumRepository
from server.repositories.subject_repository import SubjectNotFound, SubjectRepository
from server.services.email.email_service import (
    FORUM_POST_REPORTED_SUBJECT,
    EmailService,
)
from server.services.gmail_service import gmail_login, gmail_send_message
from server.utils.must_be_int import must_be_int

embed = Body(..., embed=True)

router = APIRouter(prefix="/mobile/forum", tags=["Forum", "Mobile"])


@router.get("/posts")
async def get_posts(
    session: SessionDep,
    subject_id: int,
    user_id: int | None = None,
    filter_tags: list[int] = Query(None),
    search_keyword: str | None = None,
) -> list[ForumPostReplyResponse]:
    """Get all posts by tags, also gets all posts reaction information based on the user_id
    If a search keyword is present in the request, return posts with that word
    """
    posts = ForumRepository.get_all_posts(
        subject_id=subject_id,
        filter_tags=filter_tags,
        search_keyword=search_keyword,
        session=session,
    )

    return ForumPostReplyResponse.from_forum_post_reply_list(posts, user_id, session)


@router.post("/posts")
async def create_forum_post(
    input: ForumPostRegister,
    session: SessionDep,
    user: MobileUserDep,
) -> ForumPostResponse:
    """Create a forum post with provided tags. The General Forum is associeted with subject_id == -1"""
    check_acting_as(user, input.user_id)

    if input.subject_id == -1:
        globalForumSubject: Subject
        try:
            globalForumSubject = SubjectRepository.get_by_name(
                name="Forum Geral", session=session
            )
        except SubjectNotFound:
            globalForumSubject = SubjectRepository.create_general_forum(
                id=input.subject_id, name="Forum Geral", session=session
            )

        input.subject_id = must_be_int(globalForumSubject.id)
        input.class_id = None

    forum_post = ForumRepository.create(
        input=to_forumpost_model(input), session=session
    )

    return ForumPostResponse.from_forum_post(input.user_id, forum_post, session)


@router.delete("/posts/{post_id}")
async def delete_forum_post(
    post_id: int, session: SessionDep, user: MobileUserDep
) -> None:
    """Soft delete (disable) a forum post (its author only: the mobile user of
    the Google token)"""
    post = session.get(ForumPost, post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post não encontrado")
    if user.id != post.user_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Só quem escreveu o post pode excluí-lo"
        )
    ForumRepository.disable_post(post_id=post_id, session=session)


@router.post("/report")
async def report_forum_post(
    input: ForumReportRegister, session: SessionDep, user: MobileUserDep
) -> ForumPost:
    """Report forum post (as the token's user) and send e-mail to uspolis
    admin if necessary"""
    check_acting_as(user, input.user_id)
    updated_post = ForumRepository.update_forum_report_count(
        post_id=input.post_id,
        mobile_user_id=must_be_int(user.id),
        session=session,
    )

    if updated_post.report_count == 10:
        subject = session.get(Subject, updated_post.subject_id)
        send_email(updated_post, subject.code if subject else "")

    return updated_post


def send_email(post: ForumPost, subject_code: str) -> Any:
    html_content = EmailService.render_forum_post_reported(
        ForumPostReportedMail.from_post(post, subject_code)
    )
    creds = gmail_login()
    sent_email = gmail_send_message(
        creds, html_content, subject=FORUM_POST_REPORTED_SUBJECT
    )
    return sent_email


# Post Reply
@router.post("/posts/{post_id}")
async def create_forum_post_reply(
    post_id: int,
    input: ForumPostRegister,
    session: SessionDep,
    user: MobileUserDep,
) -> ForumPostReplyResponse:
    """Create forum post reply"""
    check_acting_as(user, input.user_id)
    reply = ForumRepository.create_reply(
        input=to_forumreply_model(post_id, input),
        session=session,
    )
    return ForumPostReplyResponse.from_forum_reply(reply, input.user_id, session)


@router.get("/posts/{post_id}")
async def get_forum_post_replies(
    post_id: int, user_id: int, session: SessionDep
) -> list[ForumPostReplyResponse]:
    """Get all replies from a single post"""
    replies = ForumRepository.get_all_replies(post_id=post_id, session=session)

    return ForumPostReplyResponse.from_forum_post_reply_list(replies, user_id, session)


@router.post("/posts/{post_id}/liked")
async def update_forum_post_like(
    post_id: int, input: ForumPostLike, session: SessionDep, user: MobileUserDep
) -> ForumPost:
    """Change post like reaction state (of the token's user)"""
    check_acting_as(user, input.user_id)
    like_changed_post = ForumRepository.change_forum_post_like(
        post_id=post_id,
        mobile_user_id=must_be_int(user.id),
        like_state=input.like_state,
        session=session,
    )

    return like_changed_post
