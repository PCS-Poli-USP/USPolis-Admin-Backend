import logging
from collections.abc import Callable
from datetime import datetime, timedelta

from sqlmodel import Session

from server.config import CONFIG
from server.db import engine
from server.models.http.requests.email_request_models import ApiKeyExpiringMail
from server.repositories.api_access_log_repository import ApiAccessLogRepository
from server.repositories.api_key_delivery_link_repository import (
    ApiKeyDeliveryLinkRepository,
)
from server.repositories.api_key_repository import ApiKeyRepository
from server.repositories.search_query_log_repository import SearchQueryLogRepository
from server.services.email.email_service import EmailService
from server.services.security.api_key_auth import invalidate_api_key_cache
from server.utils.brazil_datetime import BrazilDatetime

logger = logging.getLogger(__name__)

# Days before expires_at when the partner contact is warned, one email each.
API_KEY_EXPIRY_WARNING_DAYS = (30, 7, 1)


def purge_old_access_logs(session: Session) -> None:
    cutoff = BrazilDatetime.now_utc() - timedelta(
        days=CONFIG.error_metrics_retention_days
    )
    deleted = ApiAccessLogRepository.delete_older_than(cutoff=cutoff, session=session)
    logger.info("Purged %d api access log(s) older than %s", deleted, cutoff)


def purge_old_search_logs(session: Session) -> None:
    cutoff = BrazilDatetime.now_utc().date() - timedelta(
        days=CONFIG.search_log_retention_days
    )
    deleted = SearchQueryLogRepository.delete_older_than(cutoff=cutoff, session=session)
    logger.info("Purged %d search query log(s) older than %s", deleted, cutoff)


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


def _due_expiry_warning(expires_at: datetime, now: datetime) -> int:
    """The smallest warning window the key is already inside, e.g. 7 for a
    key expiring in 5 days. A missed day is caught up by the next run."""
    left = expires_at - now
    return min(d for d in API_KEY_EXPIRY_WARNING_DAYS if left <= timedelta(days=d))


def warn_expiring_api_keys(session: Session) -> None:
    """Email the contact of each client whose key expires within
    API_KEY_EXPIRY_WARNING_DAYS, with uspolis@usp.br in copy.

    `apikey.expiry_warning_days` records the warning already sent, so a run
    after a restart, or on a second worker at the same time, never repeats
    it: each key is locked (skipping keys another worker holds), rechecked,
    emailed, marked and committed on its own. A failed email leaves the key
    unmarked and is retried on the next run; a commit failing right after a
    successful email is the only way to get a duplicate."""
    now = BrazilDatetime.now_utc()
    # Commit what earlier tasks did, so per-key commits below stay small.
    session.commit()
    ids = ApiKeyRepository.get_ids_expiring_before(
        now=now,
        until=now + timedelta(days=max(API_KEY_EXPIRY_WARNING_DAYS)),
        session=session,
    )
    sent = 0
    for id in ids:
        key = ApiKeyRepository.lock_for_expiry_warning(id=id, session=session)
        if key is None or not key.is_usable(now):
            session.rollback()
            continue
        due = _due_expiry_warning(key.expires_at, now)
        if key.expiry_warning_days is not None and key.expiry_warning_days <= due:
            session.rollback()
            continue
        public_id = key.public_id
        try:
            EmailService.send_api_key_expiring_email(
                to=[key.client.contact_email],
                data=ApiKeyExpiringMail.from_key(key, now),
            )
        except Exception:
            session.rollback()
            logger.exception(
                "Failed to send the expiry warning of API key %s", public_id
            )
            continue
        key.expiry_warning_days = due
        session.add(key)
        session.commit()
        sent += 1
    logger.info("Sent %d API key expiry warning(s)", sent)


DAILY_TASKS: list[Callable[[Session], None]] = [
    purge_old_access_logs,
    purge_old_search_logs,
    expire_api_key_links,
    # Last: it commits on its own, key by key.
    warn_expiring_api_keys,
]


def run_daily_tasks() -> None:
    with Session(engine) as session:
        for task in DAILY_TASKS:
            task(session)
        session.commit()
