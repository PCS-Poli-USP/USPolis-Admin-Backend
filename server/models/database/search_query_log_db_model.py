from datetime import date, datetime

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlmodel import Field

from server.models.database.base_db_model import BaseModel


class SearchQueryLog(BaseModel, table=True):
    """Public searches of one day, aggregated per normalized query and type
    filter (see docs/SEARCH.md, "Query log").

    One row per (day, query, types): repeating a search only bumps its
    counters, so the table grows with the number of distinct queries, never
    with the number of requests. New rows are capped per client IP and per
    day (search_log_service), which bounds the table size.

    Holds no personal data on purpose: no user, IP, user agent or session id.
    Rows older than SEARCH_LOG_RETENTION_DAYS are purged daily."""

    __table_args__ = (
        UniqueConstraint(
            "day", "query", "types", name="uq_searchquerylog_day_query_types"
        ),
    )

    # Brazil date of the searches.
    day: date = Field(nullable=False)
    # normalize_query() output: lower case, no accents, single spaces.
    query: str = Field(max_length=100, nullable=False)
    # SearchEntityType values of the filter, sorted; empty means all types.
    types: list[str] = Field(
        sa_column=Column(
            postgresql.ARRAY(String()), nullable=False, server_default="{}"
        )
    )
    searches: int = Field(nullable=False)
    # Searches that returned nothing.
    empty_searches: int = Field(nullable=False)
    # Matches over the requested types in the latest search, computed by the
    # server.
    last_result_count: int = Field(nullable=False)
    last_searched_at: datetime = Field(nullable=False)
