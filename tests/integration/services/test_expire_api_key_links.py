from datetime import timedelta
from unittest.mock import MagicMock, patch

from sqlmodel import Session

from server.models.database.user_db_model import User
from server.repositories.api_key_delivery_link_repository import (
    EXPIRED_REVOKE_REASON,
)
from server.services.cron.daily_tasks import DAILY_TASKS, expire_api_key_links
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.api_key_link_status_enum import ApiKeyLinkStatus
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_delivery_link_model_factory import (
    ApiKeyDeliveryLinkModelFactory,
)
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory


def test_is_scheduled_daily() -> None:
    assert expire_api_key_links in DAILY_TASKS


@patch("server.services.cron.daily_tasks.invalidate_api_key_cache")
def test_kills_links_that_expired_unopened_and_drops_their_keys_from_cache(
    invalidate_cache: MagicMock, admin_user: User, session: Session
) -> None:
    client = ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()
    key_factory = ApiKeyModelFactory(client=client, creator=admin_user, session=session)
    key = key_factory.create_and_refresh()
    assert key_factory.last_plaintext is not None
    now = BrazilDatetime.now_utc()
    link = ApiKeyDeliveryLinkModelFactory(
        api_key=key,
        plaintext=key_factory.last_plaintext,
        creator=admin_user,
        session=session,
    ).create_and_refresh(
        created_at=now - timedelta(hours=2), expires_at=now - timedelta(hours=1)
    )

    expire_api_key_links(session)
    session.commit()
    session.refresh(link)
    session.refresh(key)

    assert link.status() == ApiKeyLinkStatus.INVALIDATED
    assert link.ciphertext is None
    assert key.revoked_reason == EXPIRED_REVOKE_REASON
    assert list(invalidate_cache.call_args.args[0]) == [key.public_id]
