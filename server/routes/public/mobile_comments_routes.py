from typing import Any

from fastapi import APIRouter, Depends

from server.deps.authenticate import admin_authenticate
from server.deps.google_auth_dep import MobileUserDep, check_acting_as
from server.deps.session_dep import SessionDep
from server.models.database.mobile_user_db_model import MobileUser
from server.models.http.requests.email_request_models import MobileCommentMail
from server.models.http.requests.mobile_comment_request_models import (
    MobileCommentRegister,
    to_comment_model,
)
from server.models.http.responses.mobile_comment_response_models import (
    MobileCommentResponse,
)
from server.repositories.mobile_comments_repository import CommentRepository
from server.services.email.email_service import MOBILE_COMMENT_SUBJECT, EmailService
from server.services.gmail_service import gmail_login, gmail_send_message

router = APIRouter(prefix="/mobile/comments", tags=["Mobile", "Comments"])


@router.post("")
async def post_comment(
    comment_input: MobileCommentRegister, session: SessionDep, user: MobileUserDep
) -> MobileCommentResponse:
    """Post a new comment, sent by a mobile user (the token's user)"""
    check_acting_as(user, comment_input.created_by)
    comment = to_comment_model(comment_input)
    comment.created_by_id = user.id

    send_email(comment.comment, comment.email, user)
    comment = CommentRepository.create(new_comment=comment, session=session)
    return MobileCommentResponse.from_model(comment)


@router.get("", dependencies=[Depends(admin_authenticate)])
def get_all_comments(session: SessionDep) -> list[MobileCommentResponse]:
    """Get all comments, sent by mobile users (admins only: they carry who
    wrote them, with email)"""
    comments = CommentRepository.get_all(session=session)
    return MobileCommentResponse.from_model_list(comments)


def send_email(
    comment: str, email: str | None = None, user: MobileUser | None = None
) -> Any:
    html_content = EmailService.render_mobile_comment(
        MobileCommentMail.from_comment(comment=comment, email=email, user=user)
    )
    creds = gmail_login()
    sent_email = gmail_send_message(creds, html_content, subject=MOBILE_COMMENT_SUBJECT)
    return sent_email
