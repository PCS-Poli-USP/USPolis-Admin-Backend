import asyncio
from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.feedback_request_models import FeedbackRegister
from server.repositories.feedback_repository import FeedbackRepository
from server.services.email.email_service import EmailService

embed = Body(..., embed=True)

router = APIRouter(prefix="/feedbacks", tags=["Feedbacks"])


@router.post("")
async def create_feedback(
    input: FeedbackRegister, user: UserDep, session: SessionDep
) -> JSONResponse:
    feedback = FeedbackRepository.create(input=input, user=user, session=session)
    session.commit()
    # asyncio.create_task(EmailService.send_feedback_email(feedback))
    return JSONResponse(
        content={"message": "Feedback criado com sucesso!"},
        status_code=status.HTTP_201_CREATED,
    )
