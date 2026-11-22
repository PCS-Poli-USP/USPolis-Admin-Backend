from datetime import timedelta

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from server.models.database.search_query_log_db_model import SearchQueryLog
from server.services.cron.daily_tasks import purge_old_search_logs
from server.utils.brazil_datetime import BrazilDatetime

URL_PREFIX = "/admin/search-logs"


def _add(session: Session, query: str, result_count: int, days_ago: int = 0) -> None:
    """One search, aggregated into its day's row like the service does."""
    searched_at = BrazilDatetime.now_utc() - timedelta(days=days_ago)
    day = searched_at.date()
    row = session.exec(
        select(SearchQueryLog).where(
            SearchQueryLog.day == day, SearchQueryLog.query == query
        )
    ).first()
    if row is None:
        row = SearchQueryLog(
            day=day,
            query=query,
            types=[],
            searches=0,
            empty_searches=0,
            last_result_count=result_count,
            last_searched_at=searched_at,
        )
    row.searches += 1
    row.empty_searches += 1 if result_count == 0 else 0
    if searched_at >= row.last_searched_at:
        row.last_result_count = result_count
        row.last_searched_at = searched_at
    session.add(row)
    session.flush()


def _seed(session: Session) -> None:
    _add(session, "calculo", 12, days_ago=2)
    _add(session, "calculo", 10, days_ago=1)
    _add(session, "calculo", 11)
    _add(session, "calculo", 11)
    _add(session, "calculo", 11, days_ago=29)  # last day of the 30-day window
    _add(session, "bandejao", 0, days_ago=4)
    _add(session, "bandejao", 0, days_ago=3)
    _add(session, "bandejao", 0)
    _add(session, "monitoria fisica", 0, days_ago=1)
    _add(session, "monitoria fisica", 4)
    _add(session, "biblioteca", 0, days_ago=60)  # outside the default 30 days
    session.commit()


class TestSearchLogSummary:
    def test_groups_by_query_most_searched_first(
        self, client: TestClient, session: Session
    ) -> None:
        _seed(session)

        response = client.get(f"{URL_PREFIX}/summary")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["since_days"] == 30
        assert data["total_searches"] == 10
        assert data["distinct_queries"] == 3
        assert data["empty_searches"] == 4
        queries = data["queries"]
        assert [q["query"] for q in queries] == [
            "calculo",
            "bandejao",
            "monitoria fisica",
        ]
        assert queries[0]["searches"] == 5
        assert queries[0]["empty_searches"] == 0
        assert queries[0]["last_result_count"] == 11
        # Returned nothing yesterday, but something today.
        assert queries[2]["empty_searches"] == 1
        assert queries[2]["last_result_count"] == 4

    def test_only_empty_lists_queries_that_returned_nothing(
        self, client: TestClient, session: Session
    ) -> None:
        _seed(session)

        data = client.get(f"{URL_PREFIX}/summary", params={"only_empty": True}).json()

        assert [q["query"] for q in data["queries"]] == ["bandejao", "monitoria fisica"]

    def test_days_widens_the_window(self, client: TestClient, session: Session) -> None:
        _seed(session)

        data = client.get(f"{URL_PREFIX}/summary", params={"days": 90}).json()

        assert data["total_searches"] == 11
        assert "biblioteca" in {q["query"] for q in data["queries"]}

    def test_requires_admin(self, common_client: TestClient) -> None:
        response = common_client.get(f"{URL_PREFIX}/summary")
        assert response.status_code == status.HTTP_403_FORBIDDEN


def test_purge_removes_logs_past_retention(session: Session) -> None:
    _add(session, "antiga", 0, days_ago=400)
    _add(session, "recente", 3, days_ago=10)
    session.commit()

    purge_old_search_logs(session)
    session.commit()

    assert [log.query for log in session.exec(select(SearchQueryLog))] == ["recente"]


def test_summary_without_logs_is_all_zero(client: TestClient) -> None:
    data = client.get(f"{URL_PREFIX}/summary").json()

    assert (
        data["total_searches"],
        data["distinct_queries"],
        data["empty_searches"],
    ) == (
        0,
        0,
        0,
    )
    assert data["queries"] == []
