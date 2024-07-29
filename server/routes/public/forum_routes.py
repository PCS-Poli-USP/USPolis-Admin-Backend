from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.requests.forum_request_models import (
    ForumPostRegister,
    to_forumpost_model,
    ForumReportRegister
)
from server.models.http.responses.forum_post_response import (
    ForumPostResponse,
)
from server.repositories.forum_repository import ForumRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/mobile/forum", tags=["Forum"])

@router.get("/posts")
async def get_posts(class_id: int, session: SessionDep) -> list[ForumPostResponse]:
    """Get all posts"""
    posts = ForumRepository.get_all_posts(class_id=class_id, session=session)
    return ForumPostResponse.from_forum_post_list(posts)

@router.post("/posts")
async def create_forum_post(input: ForumPostRegister, session: SessionDep) -> ForumPostResponse:
    """Create forum post"""
    forum_post = ForumRepository.create(
        input = to_forumpost_model(input),
        session = session,
    ) 
    return ForumPostResponse.from_forum_post(forum_post)

@router.post("/report-post")
async def report_forum_post(input: ForumReportRegister, session: SessionDep) :
    """Report forum post and send e-mail to uspolis admin if necessary"""     
    updated_post = ForumRepository.update_forum_report_count(
        post_id = input.post_id,
        mobile_user_id = input.user_id,
        session = session,
    )

    if updated_post.report_count == 10:
        #TODO: Send EMail To Warning A Report
       pass


    return updated_post

