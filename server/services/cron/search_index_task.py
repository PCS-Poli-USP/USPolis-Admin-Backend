import logging

from sqlmodel import Session

from server.db import engine
from server.repositories.search_repository import SearchRepository

logger = logging.getLogger(__name__)


def refresh_search_index() -> None:
    """Rebuild the public search index. Every worker runs this on a timer;
    the advisory lock in SearchRepository.refresh makes the others skip while
    one is refreshing. Errors are logged, never raised, so the timer survives."""
    try:
        with Session(engine) as session:
            refreshed = SearchRepository.refresh(session=session)
        if refreshed:
            logger.info("Search index refreshed")
    except Exception:
        logger.exception("Search index refresh failed")
