from typing import Annotated
from typing import Any
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
from server.services.gmail_service import gmail_login, gmail_send_message

embed = Body(..., embed=True)

router = APIRouter(prefix="/mobile/forum", tags=["Forum", "Mobile"])


@router.get("/posts")
async def get_posts(subject_id: int, session: SessionDep) -> list[ForumPostResponse]:
    """Get all posts"""
    posts = ForumRepository.get_all_posts(subject_id=subject_id, session=session)
    return ForumPostResponse.from_forum_post_list(posts)


@router.post("/posts")
async def create_forum_post(
    input: ForumPostRegister, session: SessionDep, authorization: str = Header(None),
) -> ForumPostResponse:
    """Create a forum post"""
    # authenticate before creating and saving a post
    authenticate_with_google(authorization)

    forum_post = ForumRepository.create(
        input=to_forumpost_model(input),
        session=session
    )
    return ForumPostResponse.from_forum_post(forum_post)

@router.delete("/posts/{post_id}")
async def delete_forum_post(
    post_id: int,
    session: SessionDep,
    authorization: str = Header(None)
):
    """Soft delete (disable) a forum post"""
    # authenticate (perhaps its better to use cognito and the admin)
    authenticate_with_google(authorization)

    ForumRepository.disable_post(
        post_id=post_id,
        session=session
    )

@router.post("/report")
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
        send_email(updated_post)

    return updated_post

def send_email(
    post: ForumPost
) -> Any:
    html_content = f"""
        <h1> Um postagem foi denunciada {post.report_count} vezes! </h1>
        <h2> Dados da postagem </h2>
        <p>Post ID: {post.id}</p>
        <p>Conteúdo: {post.content}</p>
        <p>Autor da postagem: {post.user}</p>
    """
    creds = gmail_login()
    sent_email = gmail_send_message(creds, html_content)
    return sent_email

# Post Reply
@router.post("/posts/{post_id}")
async def create_forum_post_reply(
    post_id: int,
    input: ForumPostRegister, 
    session: SessionDep,
    authorization: str = Header(None),
) -> ForumPostReplyResponse:
    """Create forum post reply"""
    
    # authenticate before creating and saving reply
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
