import pytest

from server.models.http.requests.feedback_request_models import (
    FeedbackInvalidInput,
    FeedbackRegister,
)


class TestFeedbackRegister:
    def test_valid_input_passes(self) -> None:
        feedback = FeedbackRegister(title="Sugestão", message="Adicionar filtro")

        assert feedback.title == "Sugestão"

    def test_rejects_an_empty_title(self) -> None:
        with pytest.raises(FeedbackInvalidInput):
            FeedbackRegister(title="", message="Adicionar filtro")

    def test_rejects_an_empty_message(self) -> None:
        with pytest.raises(FeedbackInvalidInput):
            FeedbackRegister(title="Sugestão", message="")
