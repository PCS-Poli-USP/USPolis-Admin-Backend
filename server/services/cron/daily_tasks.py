import logging
from collections.abc import Callable
from datetime import timedelta

from sqlmodel import Session

from server.config import CONFIG
from server.db import engine
from server.repositories.api_access_log_repository import ApiAccessLogRepository
from server.repositories.api_key_delivery_link_repository import (
    ApiKeyDeliveryLinkRepository,
)
from server.services.security.api_key_auth import invalidate_api_key_cache
from server.utils.brazil_datetime import BrazilDatetime

logger = logging.getLogger(__name__)


def purge_old_access_logs(session: Session) -> None:
    cutoff = BrazilDatetime.now_utc() - timedelta(
        days=CONFIG.error_metrics_retention_days
    )
    deleted = ApiAccessLogRepository.delete_older_than(cutoff=cutoff, session=session)
    logger.info("Purged %d api access log(s) older than %s", deleted, cutoff)


def expire_api_key_links(session: Session) -> None:
    """Wipe the sealed keys of delivery links that expired unopened and
    revoke those keys, which nobody received. Reveal checks expiry itself,
    so this is cleanup, not enforcement."""
    links = ApiKeyDeliveryLinkRepository.expire_pending(
        now=BrazilDatetime.now_utc(), session=session
    )
    session.flush()
    invalidate_api_key_cache(link.api_key.public_id for link in links)
    logger.info("Expired %d unopened API key delivery link(s)", len(links))


DAILY_TASKS: list[Callable[[Session], None]] = [
    purge_old_access_logs,
    expire_api_key_links,
]


def run_daily_tasks() -> None:
    with Session(engine) as session:
        for task in DAILY_TASKS:
            task(session)
        session.commit()
