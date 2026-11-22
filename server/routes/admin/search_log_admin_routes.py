from datetime import timedelta

from fastapi import APIRouter, Query

from server.config import CONFIG
from server.deps.session_dep import SessionDep
from server.models.http.responses.search_response_models import (
    SearchLogSummaryResponse,
    SearchQueryStatResponse,
)
from server.repositories.search_query_log_repository import SearchQueryLogRepository
from server.utils.brazil_datetime import BrazilDatetime

router = APIRouter(prefix="/search-logs", tags=["Search Logs"])


@router.get("/summary")
def get_search_log_summary(
    session: SessionDep,
    days: int = Query(default=30, ge=1, le=CONFIG.search_log_retention_days),
    only_empty: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=500),
) -> SearchLogSummaryResponse:
    """What people searched in the last `days` days, grouped by normalized
    query. `only_empty=true` lists the queries that returned nothing at least
    once, most frequent first: the gaps of the search (missing synonyms,
    typos the index does not tolerate, data that is not public yet)."""
    # Today plus the days - 1 before it.
    since = BrazilDatetime.now_utc().date() - timedelta(days=days - 1)
    totals = SearchQueryLogRepository.get_totals(since=since, session=session)
    stats = SearchQueryLogRepository.get_stats(
        since=since, only_empty=only_empty, limit=limit, session=session
    )
    return SearchLogSummaryResponse(
        since_days=days,
        total_searches=totals.searches,
        distinct_queries=totals.distinct_queries,
        empty_searches=totals.empty_searches,
        queries=[SearchQueryStatResponse.from_stat(s) for s in stats],
    )
