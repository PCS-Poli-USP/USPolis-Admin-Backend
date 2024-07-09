from fastapi import APIRouter, Depends, Body, Response

from server.deps.session_dep import SessionDep
from server.models.http.requests.forum_request_models import (
    ForumPostRegister
)
from server.models.http.responses.forum_post_response import (
    ForumPostResponse,
)


embed = Body(..., embed=True)

router = APIRouter(prefix="/forum", tags=["Forum"])

@router.get("/{class_id}")
async def get_posts(class_id: int, session: SessionDep) -> list[ForumPostResponse]:
    """Get all posts"""
    posts = ForumRepository.get_all_posts(class_id=class_id, session=session)
    return ForumPostResponse.func(posts)

@router.post("/{class_id}")
async def create_forum_post(class_id: int, input: ForumPostRegister, session: SessionDep) -> ForumPostResponse:
    """Create forum post"""
    forum_post = ForumRepository.create(
        input = input,
        session = session,
    ) 
    return ForumPostResponse.from_forum_post(forum_post)

@router.get("")
async def foo():
    """Get all posts"""
    
    return {'Hello':' World'}