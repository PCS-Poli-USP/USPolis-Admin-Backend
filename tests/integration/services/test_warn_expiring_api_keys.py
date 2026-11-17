from collections.abc import Generator
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.user_db_model import User
from server.services.cron.daily_tasks import DAILY_TASKS, warn_expiring_api_keys
from server.utils.brazil_datetime import BrazilDatetime
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory

SEND = "server.services.cron.daily_tasks.EmailService.send_api_key_expiring_email"


@pytest.fixture
def send() -> Generator[MagicMock, None, None]:
    with patch(SEND) as send:
        yield send


@pytest.fixture
def api_client(admin_user: User, session: Session) -> ApiClient:
    return ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()


@pytest.fixture
def key_factory(
    admin_user: User, session: Session, api_client: ApiClient
) -> ApiKeyModelFactory:
    return ApiKeyModelFactory(client=api_client, creator=admin_user, session=session)


def key_expiring_in(factory: ApiKeyModelFactory, left: timedelta) -> ApiKey:
    now = BrazilDatetime.now_utc()
    return factory.create_and_refresh(
        created_at=now - timedelta(days=60), expires_at=now + left
    )


def warned(key: ApiKey, session: Session) -> int | None:
    session.refresh(key)
    return key.expiry_warning_days


def test_is_scheduled_daily_and_last() -> None:
    # It commits key by key, which would also commit later tasks halfway.
    assert DAILY_TASKS[-1] is warn_expiring_api_keys


def test_warns_the_client_contact_once_per_window(
    send: MagicMock,
    session: Session,
    api_client: ApiClient,
    key_factory: ApiKeyModelFactory,
) -> None:
    key = key_expiring_in(key_factory, timedelta(days=20))

    warn_expiring_api_keys(session)
    warn_expiring_api_keys(session)  # e.g. after a restart

    send.assert_called_once()
    assert send.call_args.kwargs["to"] == [api_client.contact_email]
    data = send.call_args.kwargs["data"]
    assert data.key_name == key.name
    assert data.public_id == key.public_id
    assert data.client_name == api_client.name
    assert warned(key, session) == 30


@pytest.mark.parametrize(
    ("left", "window"),
    [
        (timedelta(days=30), 30),
        (timedelta(days=7), 7),
        (timedelta(days=3), 7),
        (timedelta(hours=20), 1),
    ],
)
def test_sends_the_smallest_window_the_key_is_in(
    send: MagicMock,
    session: Session,
    key_factory: ApiKeyModelFactory,
    left: timedelta,
    window: int,
) -> None:
    key = key_expiring_in(key_factory, left)

    warn_expiring_api_keys(session)

    send.assert_called_once()
    assert warned(key, session) == window


def test_moves_to_the_next_window_after_an_earlier_warning(
    send: MagicMock, session: Session, key_factory: ApiKeyModelFactory
) -> None:
    key = key_expiring_in(key_factory, timedelta(days=5))
    key.expiry_warning_days = 30
    session.add(key)
    session.commit()

    warn_expiring_api_keys(session)
    warn_expiring_api_keys(session)

    send.assert_called_once()
    assert warned(key, session) == 7


def test_ignores_keys_that_dont_need_a_warning(
    send: MagicMock,
    admin_user: User,
    session: Session,
    key_factory: ApiKeyModelFactory,
) -> None:
    now = BrazilDatetime.now_utc()
    key_expiring_in(key_factory, timedelta(days=31))
    key_expiring_in(key_factory, timedelta(days=-1))
    revoked = key_expiring_in(key_factory, timedelta(days=5))
    revoked.revoked_at = now
    session.add(revoked)
    inactive_client = ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh(is_active=False)
    key_expiring_in(
        ApiKeyModelFactory(client=inactive_client, creator=admin_user, session=session),
        timedelta(days=5),
    )
    session.commit()

    warn_expiring_api_keys(session)

    send.assert_not_called()


def test_a_failed_email_is_retried_on_the_next_run_and_others_still_go(
    send: MagicMock, session: Session, key_factory: ApiKeyModelFactory
) -> None:
    failing = key_expiring_in(key_factory, timedelta(days=2))
    other = key_expiring_in(key_factory, timedelta(days=10))
    send.side_effect = [RuntimeError("SMTP down"), None]

    warn_expiring_api_keys(session)

    assert send.call_count == 2
    assert warned(failing, session) is None
    assert warned(other, session) == 30

    send.side_effect = None
    warn_expiring_api_keys(session)

    assert send.call_count == 3
    assert warned(failing, session) == 7
