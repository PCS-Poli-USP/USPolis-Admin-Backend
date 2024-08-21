from typing import Annotated
from fastapi import APIRouter, Body, Header

from server.deps.session_dep import SessionDep
from server.models.database.forum_db_model import ForumPost
from server.models.http.requests.forum_request_models import (
    ForumPostRegister,
    to_forumpost_model,
    ForumReportRegister,
    to_forumreply_model,
)
from server.models.http.responses.forum_post_response import (
    ForumPostReplyResponse,
    ForumPostResponse,
)
from server.repositories.forum_repository import ForumRepository
from server.utils.google_auth_utils import authenticate_with_google

embed = Body(..., embed=True)

router = APIRouter(prefix="/mobile/forum", tags=["Forum"])


@router.get("/posts")
async def get_posts(subject_id: int, session: SessionDep) -> list[ForumPostResponse]:
    """Get all posts"""
    posts = ForumRepository.get_all_posts(subject_id=subject_id, session=session)
    return ForumPostResponse.from_forum_post_list(posts)


@router.post("/posts")
async def create_forum_post(
    input: ForumPostRegister, session: SessionDep
) -> ForumPostResponse:
    """Create forum post"""
    forum_post = ForumRepository.create(
        input=to_forumpost_model(input),
        session=session,
    )
    return ForumPostResponse.from_forum_post(forum_post)


@router.post("/report-post")
async def report_forum_post(
    input: ForumReportRegister, session: SessionDep
) -> ForumPost:
    """Report forum post and send e-mail to uspolis admin if necessary"""
    updated_post = ForumRepository.update_forum_report_count(
        post_id=input.post_id,
        mobile_user_id=input.user_id,
        session=session,
    )

    if updated_post.report_count == 10:
        # TODO: Send EMail To Warning A Report
        pass

    return updated_post

# Post Reply

@router.post("/posts/{post_id}")
async def create_forum_post_reply(
    post_id: int,
    input: ForumPostRegister, session: SessionDep,
    authorization: str = Header(None),
) -> ForumPostReplyResponse:
    """Create forum post reply"""
    
    # authenticate before
    authenticate_with_google(authorization)

    reply = ForumRepository.create_reply(
        input=to_forumreply_model(post_id, input),
        session=session,
    )
    return ForumPostReplyResponse.from_forum_reply(reply)

@router.get("/posts/{post_id}")
async def get_forum_post_replies(
    post_id: int, session: SessionDep
) -> list[ForumPostReplyResponse]:
    """Get all replies from a single post"""
    replies = ForumRepository.get_all_replies(post_id=post_id, session=session)
    return ForumPostReplyResponse.from_forum_post_reply_list(replies)
