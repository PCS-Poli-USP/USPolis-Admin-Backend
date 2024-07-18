from datetime import datetime
import os
from fastapi import APIRouter

#from sendgrid import SendGridAPIClient
#from sendgrid.helpers.mail import Mail
from server.deps.session_dep import SessionDep
from server.routes.public.dtos.mobile_comment_dto import MobileCommentRegister, MobileCommentResponse

router = APIRouter(prefix="/mobile/comments", tags=["Mobile","Comments"])

@router.post("")
async def post_comment(comment_input: MobileCommentRegister, session: SessionDep):
    """Post a new comment, sent by a mobile user"""
    print(comment_input)
    return MobileCommentResponse(
        comment=comment_input.comment,
        email=comment_input.email,
        created_at=datetime.now()
    )

def send_email(comment: str, email: str = None):
    email_message = Mail(
        to_emails="uspolis@usp.br",
        from_email="uspolis@usp.br",
        subject="Comentário no app USPolis",
        html_content=f"""
            <p>Email: {email if email else "Não informado"}</p>
            <p>Comentário: {comment}</p>
        """
    )

    try:
        api_key = os.environ.get("SENDGRID_API_KEY")
        email_client = SendGridAPIClient(api_key)
        email_client.send(email_message)
        print("E-mail enviado com sucesso!")

    except Exception as err:
        print(f"Erro no envio de email: {err}")