from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.feedback_response_models import FeedbackResponse
from server.repositories.feedback_repository import FeedbackRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/feedbacks", tags=["Feedbacks"])


@router.get("")
def get_all_feedbacks(session: SessionDep) -> list[FeedbackResponse]:
    feedbacks = FeedbackRepository.get_all(session=session)
    return FeedbackResponse.from_feedback_list(feedbacks)
