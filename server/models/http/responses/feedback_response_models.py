from datetime import datetime
from pydantic import BaseModel

from server.models.database.feedback_db_model import Feedback
from server.utils.must_be_int import must_be_int


class FeedbackResponse(BaseModel):
    id: int
    title: str
    message: str
    created_at: datetime
    user_id: int
    user_email: str
    user_name: str

    @classmethod
    def from_feedback(cls, feedback: Feedback) -> "FeedbackResponse":
        return FeedbackResponse(
            id=must_be_int(feedback.id),
            title=feedback.title,
            message=feedback.message,
            created_at=feedback.created_at,
            user_id=feedback.user_id,
            user_name=feedback.user.name,
            user_email=feedback.user.email,
        )

    @classmethod
    def from_feedback_list(cls, feedbacks: list[Feedback]) -> list["FeedbackResponse"]:
        return [FeedbackResponse.from_feedback(fed) for fed in feedbacks]
