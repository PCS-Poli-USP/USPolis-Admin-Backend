from typing import Any
from fastapi import APIRouter

from server.deps.session_dep import SessionDep
from server.models.database.mobile_user_db_model import MobileUser
from server.models.http.requests.mobile_comment_request_models import (
    MobileCommentRegister,
    to_comment_model,
)
from server.repositories.mobile_comments_repository import CommentRepository
from server.models.http.responses.mobile_comment_response_models import (
    MobileCommentResponse,
)
from server.repositories.mobile_user_repository import MobileUserRepository
from server.services.gmail_service import gmail_login, gmail_send_message
from server.utils.must_be_int import must_be_int

router = APIRouter(prefix="/mobile/comments", tags=["Mobile", "Comments"])


@router.post("")
async def post_comment(
    comment_input: MobileCommentRegister, session: SessionDep
) -> MobileCommentResponse:
    """Post a new comment, sent by a mobile user"""
    comment = to_comment_model(comment_input)
    if comment.created_by_id is not None:
        user = MobileUserRepository.get_user_by_id(
            id=must_be_int(comment.created_by_id), session=session
        )
    else:
        user = None

    send_email(comment.comment, comment.email, user)
    comment = CommentRepository.create(
        new_comment=to_comment_model(comment_input), session=session
    )
    return MobileCommentResponse.from_model(comment)


@router.get("")
def get_all_comments(session: SessionDep) -> list[MobileCommentResponse]:
    """Get all comments, sent by mobile users"""
    comments = CommentRepository.get_all(session=session)
    return MobileCommentResponse.from_model_list(comments)


def send_email(
    comment: str, email: str | None = None, user: MobileUser | None = None
) -> Any:
    html_content = f"""
        <h1> Dados do comentário </h1>
        <p>Email: {email if email else "Não informado"}</p>
        <p>Comentário: {comment}</p>
    """
    if user is not None:
        html_content += f"""
        <h1> Dados do usuário </h1>
        <p>User id: {user.id}
        """
    creds = gmail_login()
    sent_email = gmail_send_message(creds, html_content)
    return sent_email
