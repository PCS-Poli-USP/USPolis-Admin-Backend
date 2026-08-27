import logging
from collections.abc import Callable
from datetime import timedelta

from sqlmodel import Session

from server.config import CONFIG
from server.db import engine
from server.repositories.api_access_log_repository import ApiAccessLogRepository
from server.utils.brazil_datetime import BrazilDatetime

logger = logging.getLogger(__name__)


def purge_old_access_logs(session: Session) -> None:
    cutoff = BrazilDatetime.now_utc() - timedelta(
        days=CONFIG.error_metrics_retention_days
    )
    deleted = ApiAccessLogRepository.delete_older_than(cutoff=cutoff, session=session)
    logger.info("Purged %d api access log(s) older than %s", deleted, cutoff)


DAILY_TASKS: list[Callable[[Session], None]] = [
    purge_old_access_logs,
]


def run_daily_tasks() -> None:
    with Session(engine) as session:
        for task in DAILY_TASKS:
            task(session)
        session.commit()
