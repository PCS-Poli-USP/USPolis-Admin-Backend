from server.models.http.responses.feedback_response_models import FeedbackResponse
from tests.utils.academic_test_utils import make_user
from tests.utils.feedback_test_utils import make_feedback


class TestFeedbackResponse:
    def test_from_feedback(self) -> None:
        user = make_user(name="Ana")
        feedback = make_feedback(user=user, title="Sugestão")

        data = FeedbackResponse.from_feedback(feedback)

        assert data.id == feedback.id
        assert data.title == "Sugestão"
        assert data.user_id == user.id
        assert data.user_name == "Ana"
        assert data.user_email == user.email
        assert data.user_picture_url == user.picture_url

    def test_from_feedback_list(self) -> None:
        user = make_user()
        feedback1 = make_feedback(user=user)
        feedback2 = make_feedback(user=user)

        data = FeedbackResponse.from_feedback_list([feedback1, feedback2])

        assert [d.id for d in data] == [feedback1.id, feedback2.id]
