from datetime import datetime

from server.models.database.feedback_db_model import Feedback
from server.models.database.user_db_model import User
from server.models.http.responses.feedback_response_models import FeedbackResponse
from tests.utils.academic_test_utils import make_user

_next_id = iter(range(1, 1_000_000))


def _make_feedback(*, user: User) -> Feedback:
    feedback = Feedback(
        id=next(_next_id),
        user_id=user.id,
        title="Sugestão",
        message="Poderia adicionar filtro por prédio",
        created_at=datetime(2025, 1, 1),
    )
    feedback.user = user
    return feedback


class TestFeedbackResponse:
    def test_from_feedback(self) -> None:
        user = make_user(name="Ana")
        feedback = _make_feedback(user=user)

        data = FeedbackResponse.from_feedback(feedback)

        assert data.id == feedback.id
        assert data.title == "Sugestão"
        assert data.user_id == user.id
        assert data.user_name == "Ana"
        assert data.user_email == user.email
        assert data.user_picture_url == user.picture_url

    def test_from_feedback_list(self) -> None:
        user = make_user()
        feedback1 = _make_feedback(user=user)
        feedback2 = _make_feedback(user=user)

        data = FeedbackResponse.from_feedback_list([feedback1, feedback2])

        assert [d.id for d in data] == [feedback1.id, feedback2.id]
