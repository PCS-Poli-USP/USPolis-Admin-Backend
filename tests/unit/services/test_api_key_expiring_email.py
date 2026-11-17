from collections.abc import Generator
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.http.requests.email_request_models import (
    ApiKeyExpiringMail,
    MailSend,
)
from server.services.email.email_service import SYSTEM_LIST, EmailService

EMAIL_SERVICE = "server.services.email.email_service"
NOW = datetime(2026, 11, 16, 0, 0)


def mail(**overrides: str) -> ApiKeyExpiringMail:
    return ApiKeyExpiringMail(
        **{
            "contact_name": "Ana",
            "client_name": "Parceiro X",
            "key_name": "Produção",
            "public_id": "a1b2c3d4e5f60718",
            "expires_at": "23/11/2026 às 14:00",
            "expires_in": "em 7 dias",
            **overrides,
        }
    )


@pytest.fixture
def send() -> Generator[MagicMock, None, None]:
    with patch(f"{EMAIL_SERVICE}.EmailService.send_email_or_raise") as send:
        yield send


@pytest.mark.parametrize(
    ("expires_at", "expires_in"),
    [
        (datetime(2026, 11, 16, 23, 0), "hoje"),
        (datetime(2026, 11, 17, 9, 0), "amanhã"),
        (datetime(2026, 11, 23, 14, 0), "em 7 dias"),
    ],
)
def test_mail_counts_calendar_days(expires_at: datetime, expires_in: str) -> None:
    key = ApiKey(name="Produção", public_id="a1b2c3d4e5f60718", expires_at=expires_at)
    key.client = ApiClient(name="Parceiro X", contact_name="Ana", contact_email="a@x")

    data = ApiKeyExpiringMail.from_key(key, NOW)

    assert data.expires_in == expires_in
    assert data.expires_at == expires_at.strftime("%d/%m/%Y às %H:%M")


def test_goes_to_the_contact_with_uspolis_in_copy(send: MagicMock) -> None:
    with patch(f"{EMAIL_SERVICE}.SYSTEM_MODE", False):
        EmailService.send_api_key_expiring_email(["ana@parceiro.com"], mail())

    sent: MailSend = send.call_args.args[0]
    assert sent.to == ["ana@parceiro.com"]
    assert sent.cc == ["uspolis@usp.br"]
    assert sent.subject == "Sua chave da API expira em 7 dias - USPolis"
    assert "Produção" in sent.body
    assert "a1b2c3d4e5f60718" in sent.body
    assert "23/11/2026 às 14:00" in sent.body


def test_outside_production_only_uspolis_gets_it(send: MagicMock) -> None:
    with patch(f"{EMAIL_SERVICE}.SYSTEM_MODE", True):
        EmailService.send_api_key_expiring_email(["ana@parceiro.com"], mail())

    sent: MailSend = send.call_args.args[0]
    assert sent.to == SYSTEM_LIST
    assert sent.cc == []


def test_send_email_or_raise_puts_cc_in_the_message() -> None:
    with patch(f"{EMAIL_SERVICE}.SMTP_SSL") as smtp_cls:
        EmailService.send_email_or_raise(
            MailSend(to=["a@x"], cc=["uspolis@usp.br"], subject="s", body="b")
        )

    smtp = smtp_cls.return_value.__enter__.return_value
    message = smtp.send_message.call_args.args[0]
    assert message["To"] == "a@x"
    assert message["Cc"] == "uspolis@usp.br"
