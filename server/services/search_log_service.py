"""Recording of the anonymous search query log, with its flood guards.

The log is fed by a public endpoint, so anyone can write to it. Three things
keep that from flooding the database:

1. Aggregation: one row per (Brazil day, normalized query, type filter).
   Repeating a query only bumps counters on its row, so requests alone never
   grow the table; only *distinct* queries do.
2. Per-IP quota: one client IP may add at most
   SEARCH_LOG_MAX_NEW_QUERIES_PER_IP_PER_DAY new rows per day. Counted in
   Redis like the rate limiter (IPv6 grouped by /64), with a key that expires
   after two days; the IP never reaches the database.
3. Daily cap: at most SEARCH_LOG_MAX_NEW_QUERIES_PER_DAY new rows per day for
   everyone. Checked in Postgres, so it holds even without Redis. With the
   retention, this bounds the table at cap x SEARCH_LOG_RETENTION_DAYS rows.

A dropped search is never an error for the client: the search itself already
happened, only its record is lost. On top of this, every request still goes
through the API-wide per-IP rate limit.
"""

import logging
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from sqlmodel import Session

from server.config import CONFIG
from server.repositories.search_query_log_repository import (
    SearchQueryLogRepository,
    normalize_log_query,
    normalize_log_types,
)
from server.repositories.search_repository import SearchRepository
from server.services.rate_limiter import client_identity
from server.services.redis_client import get_redis
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.search_entity_type import SearchEntityType

logger = logging.getLogger(__name__)

# Keys live a bit longer than the day they count, so a request right after
# midnight never sees the previous day's counter expire mid-day.
IP_QUOTA_KEY_TTL_SECONDS = 2 * 86_400


class SearchLogOutcome(str, Enum):
    RECORDED = "recorded"  # new row, or one more search on an existing row
    SKIPPED_PRIVATE = "skipped_private"  # looks like personal data
    SKIPPED_DAILY_CAP = "skipped_daily_cap"
    SKIPPED_IP_QUOTA = "skipped_ip_quota"


@dataclass
class _WarnedDays:
    """Last day each cap was logged as reached, per worker: during a flood
    the cap is hit on every request, and one warning per day is enough."""

    days: dict[SearchLogOutcome, date] = field(default_factory=dict)

    def first_today(self, outcome: SearchLogOutcome, day: date) -> bool:
        if self.days.get(outcome) == day:
            return False
        self.days[outcome] = day
        return True


_warned = _WarnedDays()


def ip_quota_key(host: str | None, day: date) -> str:
    return f"sl:ip:{client_identity(host) if host else 'unknown'}:{day.isoformat()}"


async def take_new_query_slot(host: str | None, day: date) -> bool:
    """Spend one of the client's new-query slots of `day`. True while the
    client is within SEARCH_LOG_MAX_NEW_QUERIES_PER_IP_PER_DAY.

    Fails open without Redis (not configured or unreachable), like the rate
    limiter: the daily cap, checked in Postgres, still bounds the table."""
    redis = get_redis()
    if redis is None:
        return True
    key = ip_quota_key(host, day)
    try:
        async with redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, IP_QUOTA_KEY_TTL_SECONDS)
            count, _ = await pipe.execute()
    except Exception:
        # Not only RedisError/OSError: a client bound to another event loop
        # raises RuntimeError. Recording must never fail the request.
        logger.warning(
            "Search log IP quota: Redis unavailable, not enforced", exc_info=True
        )
        return True
    return int(count) <= CONFIG.search_log_max_new_queries_per_ip_per_day


async def record_search(
    *,
    query: str,
    types: list[SearchEntityType] | None,
    host: str | None,
    session: Session,
) -> SearchLogOutcome:
    """Record one search the user settled on. The result count is computed
    here (never trusted from the client), and only when something will be
    written, so dropped searches cost no extra search."""
    normalized = normalize_log_query(query)
    if normalized is None:
        return SearchLogOutcome.SKIPPED_PRIVATE
    stored_types = normalize_log_types(types)
    now = BrazilDatetime.now_utc()  # Brazil wall clock, naive
    day = now.date()

    if not SearchQueryLogRepository.exists(
        day=day, query=normalized, types=stored_types, session=session
    ):
        # Only new rows grow the table, so only they spend quota.
        if (
            SearchQueryLogRepository.count_rows_of_day(day=day, session=session)
            >= CONFIG.search_log_max_new_queries_per_day
        ):
            if _warned.first_today(SearchLogOutcome.SKIPPED_DAILY_CAP, day):
                logger.warning(
                    "Search log: daily cap of %d new queries reached for %s",
                    CONFIG.search_log_max_new_queries_per_day,
                    day,
                )
            return SearchLogOutcome.SKIPPED_DAILY_CAP
        if not await take_new_query_slot(host, day):
            if _warned.first_today(SearchLogOutcome.SKIPPED_IP_QUOTA, day):
                logger.warning(
                    "Search log: a client reached its quota of %d new queries "
                    "for %s (logged once per day and worker)",
                    CONFIG.search_log_max_new_queries_per_ip_per_day,
                    day,
                )
            return SearchLogOutcome.SKIPPED_IP_QUOTA

    hits = SearchRepository.search(
        query=query,
        types=types or SearchEntityType.values(),
        limit_per_type=1,
        session=session,
    )
    SearchQueryLogRepository.create_or_increment(
        day=day,
        query=normalized,
        types=stored_types,
        # One hit per matching type, each carrying its type's total.
        result_count=sum(hit.total for hit in hits),
        now=now,
        session=session,
    )
    session.commit()
    return SearchLogOutcome.RECORDED
