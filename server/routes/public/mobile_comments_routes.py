from email.mime.text import MIMEText
import os
import base64
from typing import Any
from fastapi import APIRouter

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore

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
from server.utils.must_be_int import must_be_int

router = APIRouter(prefix="/mobile/comments", tags=["Mobile", "Comments"])

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]


@router.post("")
async def post_comment(
    comment_input: MobileCommentRegister, session: SessionDep
) -> MobileCommentResponse:
    """Post a new comment, sent by a mobile user"""
    comment = to_comment_model(comment_input)
    if comment.created_by_id != None:
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
async def get_all_comments(session: SessionDep) -> list[MobileCommentResponse]:
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


def gmail_login() -> Credentials:
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds  # type: ignore


def gmail_send_message(creds: Credentials, content: Any) -> Any:
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        message = MIMEText(content, "html")

        message["To"] = "uspolis@usp.br"
        message["From"] = service.users().getProfile(userId="me").execute().get("emailAddress")
        message["Subject"] = "Comentário no app USPolis"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message
