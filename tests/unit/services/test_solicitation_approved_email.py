from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from server.models.http.requests.solicitation_request_models import (
    APPROVE_MESSAGE_MAX_LENGTH,
    SolicitationApprove,
)
from server.services.email.email_service import env


def approve(**overrides: object) -> SolicitationApprove:
    return SolicitationApprove.model_validate(
        {"classroom_id": 1, "classroom_name": "B2-05", **overrides}
    )


class TestMessageField:
    def test_is_optional(self) -> None:
        assert approve().message is None

    @pytest.mark.parametrize("blank", ["", "   ", "\n"])
    def test_blank_is_none(self, blank: str) -> None:
        assert approve(message=blank).message is None

    def test_is_trimmed(self) -> None:
        assert approve(message="  Use a sala ao lado.  ").message == (
            "Use a sala ao lado."
        )

    def test_has_the_same_limit_as_the_ui(self) -> None:
        approve(message="x" * APPROVE_MESSAGE_MAX_LENGTH)
        with pytest.raises(ValidationError):
            approve(message="x" * (APPROVE_MESSAGE_MAX_LENGTH + 1))


def render(message: str | None) -> str:
    data = SimpleNamespace(
        username="Ana",
        approved_classroom="B2-05",
        message=message,
        title="Reunião",
        type="Reunião",
        building="Elétrica",
        classroom="B2-05",
        time="16:00 ~ 17:30",
        dates="26/11/2026",
        capacity=25,
    )
    return env.get_template("/solicitations/solicitation-approved.html").render(
        data=data
    )


class TestApprovedTemplate:
    def test_shows_the_message(self) -> None:
        body = render("Retire a chave na portaria.")

        assert "Mensagem de quem aprovou" in body
        assert "Retire a chave na portaria." in body

    def test_without_a_message_has_no_message_block(self) -> None:
        assert "Mensagem de quem aprovou" not in render(None)

    def test_escapes_html(self) -> None:
        body = render('<a href="http://x">clique</a>')

        assert '<a href="http://x">' not in body
        assert "&lt;a href=" in body


def test_denied_template_escapes_the_justification() -> None:
    data = SimpleNamespace(
        username="Ana",
        justification="<b>não</b>",
        title="t",
        type="t",
        building="b",
        classroom="c",
        time="t",
        dates="d",
        capacity=1,
    )
    body = env.get_template("/solicitations/solicitation-denied.html").render(data=data)

    assert "<b>não</b>" not in body
    assert "&lt;b&gt;não&lt;/b&gt;" in body
