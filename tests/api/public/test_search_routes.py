from typing import Any

import pytest
from fakeredis import FakeAsyncRedis, FakeServer
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.event_db_model import Event
from server.models.database.meeting_db_model import Meeting
from server.models.database.search_query_log_db_model import SearchQueryLog
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.repositories.search_repository import SearchRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.enums.search_entity_type import SearchEntityType
from tests.factories.model.event_model_factory import EventModelFactory
from tests.factories.model.meeting_model_factory import MeetingModelFactory

URL_PREFIX = "/search"


@pytest.fixture(name="search_data")
def search_data_fixture(
    building: Building,
    subject: Subject,
    class_: Class,
    allocated_classroom: Classroom,
    session: Session,
) -> dict[str, Any]:
    """Known names for the standard building/classroom/subject/class (the class
    is allocated in the classroom), then rebuild the search index."""
    building.name = "Biênio"
    allocated_classroom.name = "B2-04"
    subject.code = "MAC0110"
    subject.name = "Cálculo Diferencial e Integral I"
    # Same person, with and without the crawler's "(R)" (in charge) marker.
    subject.professors = ["(R) João da Silva Pereira"]
    class_.professors = ["João da Silva Pereira"]
    session.add_all([building, allocated_classroom, subject, class_])
    session.commit()
    assert SearchRepository.refresh(session=session)
    return {
        "building": building,
        "classroom": allocated_classroom,
        "subject": subject,
        "class": class_,
    }


def _search(client: TestClient, **params: Any) -> dict[str, Any]:
    response = client.get(URL_PREFIX, params=params)
    assert response.status_code == status.HTTP_200_OK, response.text
    data: dict[str, Any] = response.json()
    return data


def _group(data: dict[str, Any], type_: str) -> dict[str, Any] | None:
    return next((g for g in data["groups"] if g["type"] == type_), None)


def _related_keys(data: dict[str, Any]) -> set[str]:
    return {i["doc_key"] for g in data["top"]["related"] for i in g["items"]}


class TestSearchMatching:
    def test_query_without_accents_finds_subject_and_its_class(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="calculo")

        subject = search_data["subject"]
        assert data["top"]["doc_key"] == f"subject:{subject.id}"
        assert data["top"]["title"] == "MAC0110 - Cálculo Diferencial e Integral I"
        assert f"class:{search_data['class'].id}" in _related_keys(data)

    def test_typo_still_finds_subject(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="calclo")

        subjects = _group(data, "subject")
        assert subjects is not None
        assert subjects["items"][0]["entity_id"] == str(search_data["subject"].id)

    def test_exact_subject_code_is_the_top_result(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="mac0110")

        assert data["top"]["doc_key"] == f"subject:{search_data['subject'].id}"

    def test_partial_professor_name_finds_a_single_professor(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="joao pereira")

        assert data["top"]["type"] == "professor"
        assert data["top"]["title"] == "João da Silva Pereira"
        assert data["top"]["entity_id"] == "joao-da-silva-pereira"
        professors = _group(data, "professor")
        assert professors is not None
        # "(R) João da Silva Pereira" and "João da Silva Pereira" are one doc.
        assert professors["total"] == 1
        related = _related_keys(data)
        assert f"class:{search_data['class'].id}" in related
        assert f"subject:{search_data['subject'].id}" in related

    def test_classroom_name_links_to_building_and_allocated_class(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="B2-04")

        assert data["top"]["doc_key"] == f"classroom:{search_data['classroom'].id}"
        assert data["top"]["subtitle"] == "Biênio"
        related = _related_keys(data)
        assert f"building:{search_data['building'].id}" in related
        assert f"class:{search_data['class'].id}" in related

    def test_building_name_without_accent_links_to_its_classrooms(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="bienio")

        assert data["top"]["doc_key"] == f"building:{search_data['building'].id}"
        assert f"classroom:{search_data['classroom'].id}" in _related_keys(data)


class TestSearchParameters:
    def test_types_filter_restricts_groups(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="calculo", types=["class"])

        assert [g["type"] for g in data["groups"]] == ["class"]
        assert data["top"]["type"] == "class"

    def test_related_limit_zero_skips_expansion(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="calculo", related_limit=0)

        assert data["top"]["related"] == []

    def test_no_match_returns_empty_response(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="xyzwvqk")

        assert data == {"query": "xyzwvqk", "top": None, "groups": []}

    def test_query_with_only_symbols_returns_empty_response(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="!! &&")

        assert data["top"] is None
        assert data["groups"] == []

    @pytest.mark.parametrize("q", ["a", "x" * 101])
    def test_rejects_too_short_or_too_long_queries(
        self, public_client: TestClient, q: str
    ) -> None:
        response = public_client.get(URL_PREFIX, params={"q": q})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_rejects_unknown_type(self, public_client: TestClient) -> None:
        response = public_client.get(
            URL_PREFIX, params={"q": "calculo", "types": "user"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSearchIndex:
    def test_doc_key_is_unique_across_entity_types(
        self, search_data: dict[str, Any], session: Session
    ) -> None:
        row = (
            session.connection()
            .execute(
                text(
                    "SELECT count(*) AS total, count(DISTINCT doc_key) AS uniq, "
                    "count(DISTINCT entity_type || entity_id) AS pairs "
                    "FROM search_document"
                )
            )
            .one()
        )

        assert row.total == row.uniq == row.pairs
        # Refreshing again (CONCURRENTLY needs the unique index) still works.
        assert SearchRepository.refresh(session=session)


class TestGetSearchDocument:
    def test_returns_document_with_related(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        classroom = search_data["classroom"]
        response = public_client.get(f"{URL_PREFIX}/documents/classroom:{classroom.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["doc_key"] == f"classroom:{classroom.id}"
        assert data["title"] == "B2-04"
        related = {i["doc_key"] for g in data["related"] for i in g["items"]}
        assert f"building:{search_data['building'].id}" in related
        assert f"class:{search_data['class'].id}" in related

    def test_same_numeric_id_of_another_type_is_another_document(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        subject = search_data["subject"]
        response = public_client.get(f"{URL_PREFIX}/documents/subject:{subject.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["type"] == "subject"

    def test_unknown_document_returns_404(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/documents/classroom:999999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.fixture(name="reservation_data")
def reservation_data_fixture(
    search_data: dict[str, Any],
    admin_user: User,
    classroom: Classroom,
    event: Event,
    meeting: Meeting,
    session: Session,
) -> dict[str, Any]:
    """Approved event citing the subject code, a regular meeting, a monitoria
    booked as a meeting and a denied event; then rebuild the index."""
    event.reservation.title = "Monitoria MAC0110 de Cálculo"
    # Factories leave reservation schedules unallocated; approved ones have a room.
    event.reservation.schedule.classroom_id = classroom.id
    meeting.reservation.title = "Reunião do conselho do departamento"
    monitoring_meeting = MeetingModelFactory(
        classroom=classroom, creator=admin_user, session=session
    ).create_and_refresh()
    monitoring_meeting.reservation.title = "Monitoria de Física"
    denied_event = EventModelFactory(
        classroom=classroom, creator=admin_user, session=session
    ).create_and_refresh()
    denied_event.reservation.title = "Monitoria negada de Química"
    denied_event.reservation.status = ReservationStatus.DENIED
    session.add_all(
        [
            event.reservation,
            event.reservation.schedule,
            meeting.reservation,
            monitoring_meeting.reservation,
            denied_event.reservation,
        ]
    )
    session.commit()
    assert SearchRepository.refresh(session=session)
    return {
        **search_data,
        "event": event,
        "meeting": meeting,
        "monitoring_meeting": monitoring_meeting,
        "denied_event": denied_event,
        "reservation_classroom": classroom,
    }


class TestSearchReservations:
    def test_monitoria_finds_events_and_monitoria_meetings(
        self, public_client: TestClient, reservation_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="monitoria", limit=20)

        keys = {i["doc_key"] for g in data["groups"] for i in g["items"]}
        event_id = reservation_data["event"].reservation_id
        monitoring_id = reservation_data["monitoring_meeting"].reservation_id
        assert f"reservation:{event_id}" in keys
        assert f"reservation:{monitoring_id}" in keys
        # Denied reservations are never indexed.
        denied_id = reservation_data["denied_event"].reservation_id
        assert f"reservation:{denied_id}" not in keys
        types = {g["type"] for g in data["groups"]}
        assert {"event", "meeting"} <= types

    def test_regular_meetings_are_not_indexed(
        self, public_client: TestClient, reservation_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="conselho departamento")

        meeting_id = reservation_data["meeting"].reservation_id
        keys = {i["doc_key"] for g in data["groups"] for i in g["items"]}
        assert f"reservation:{meeting_id}" not in keys

    def test_subject_code_in_title_links_reservation_to_subject(
        self, public_client: TestClient, reservation_data: dict[str, Any]
    ) -> None:
        event_id = reservation_data["event"].reservation_id
        response = public_client.get(f"{URL_PREFIX}/documents/reservation:{event_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["type"] == "event"
        assert data["payload"]["subjects"][0]["code"] == "MAC0110"
        related = {i["doc_key"] for g in data["related"] for i in g["items"]}
        assert f"subject:{reservation_data['subject'].id}" in related

    def test_classroom_related_includes_its_reservations(
        self, public_client: TestClient, reservation_data: dict[str, Any]
    ) -> None:
        classroom = reservation_data["reservation_classroom"]
        response = public_client.get(
            f"{URL_PREFIX}/documents/classroom:{classroom.id}",
            params={"related_limit": 20},
        )

        related = {i["doc_key"] for g in response.json()["related"] for i in g["items"]}
        event_id = reservation_data["event"].reservation_id
        assert f"reservation:{event_id}" in related


def _logs(session: Session) -> list[SearchQueryLog]:
    return list(session.exec(select(SearchQueryLog).order_by(col(SearchQueryLog.id))))


def _log(client: TestClient, q: str, **body: Any) -> None:
    response = client.post(f"{URL_PREFIX}/log", json={"q": q, **body})
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text


@pytest.fixture(autouse=True)
def _no_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    """The per-IP quota runs without Redis unless a test asks for fake_redis
    (the container's real Redis client is bound to another event loop)."""
    monkeypatch.setattr("server.services.search_log_service.get_redis", lambda: None)


@pytest.fixture(name="fake_redis")
def fake_redis_fixture(monkeypatch: pytest.MonkeyPatch) -> FakeAsyncRedis:
    """Redis for the per-IP quota (the suite runs without one)."""
    redis = FakeAsyncRedis(server=FakeServer())
    monkeypatch.setattr("server.services.search_log_service.get_redis", lambda: redis)
    return redis


class TestSearchLog:
    def test_logs_normalized_query_with_server_side_count(
        self,
        public_client: TestClient,
        search_data: dict[str, Any],
        session: Session,
    ) -> None:
        _log(public_client, "  Cálculo   Diferencial ")

        [log] = _logs(session)
        assert log.query == "calculo diferencial"
        assert log.types == []
        assert log.day == BrazilDatetime.now_utc().date()
        assert (log.searches, log.empty_searches) == (1, 0)
        expected = sum(
            g["total"]
            for g in _search(public_client, q="calculo diferencial")["groups"]
        )
        assert expected > 0
        assert log.last_result_count == expected

    def test_repeating_a_query_only_bumps_its_counters(
        self, public_client: TestClient, search_data: dict[str, Any], session: Session
    ) -> None:
        for q in ("zzxqwv", "ZZXQWV", "zzxqwv"):
            _log(public_client, q)

        [log] = _logs(session)
        assert log.query == "zzxqwv"
        assert (log.searches, log.empty_searches, log.last_result_count) == (3, 3, 0)

    def test_logs_type_filter_as_its_own_row(
        self, public_client: TestClient, search_data: dict[str, Any], session: Session
    ) -> None:
        _log(public_client, "MAC0110", types=["subject", "class"])
        _log(public_client, "MAC0110")

        filtered, unfiltered = _logs(session)
        assert filtered.types == ["class", "subject"]
        assert unfiltered.types == []
        data = _search(public_client, q="MAC0110", types=["class", "subject"])
        assert filtered.last_result_count == sum(g["total"] for g in data["groups"])

    def test_all_types_is_stored_as_no_filter(
        self, public_client: TestClient, session: Session
    ) -> None:
        _log(public_client, "calculo", types=[t.value for t in SearchEntityType])
        _log(public_client, "calculo")

        [log] = _logs(session)
        assert log.types == []
        assert log.searches == 2

    @pytest.mark.parametrize(
        "q", ["joao.silva@usp.br", "123.456.789-00", "(11) 99999-1234", "12345678"]
    )
    def test_personal_data_is_accepted_but_not_stored(
        self, public_client: TestClient, session: Session, q: str
    ) -> None:
        _log(public_client, q)

        assert _logs(session) == []

    def test_rejects_invalid_body(self, public_client: TestClient) -> None:
        for body in ({"q": "a"}, {"q": "x" * 101}, {"q": "ok", "types": ["nope"]}):
            response = public_client.post(f"{URL_PREFIX}/log", json=body)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSearchLogFloodGuards:
    def test_daily_cap_stops_new_queries_but_keeps_counting_known_ones(
        self,
        public_client: TestClient,
        session: Session,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            "server.services.search_log_service.CONFIG.search_log_max_new_queries_per_day",
            2,
        )

        for q in ("primeira", "segunda", "terceira", "primeira"):
            _log(public_client, q)

        assert {(log.query, log.searches) for log in _logs(session)} == {
            ("primeira", 2),
            ("segunda", 1),
        }

    def test_ip_quota_stops_new_queries_but_keeps_counting_known_ones(
        self,
        public_client: TestClient,
        session: Session,
        fake_redis: FakeAsyncRedis,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            "server.services.search_log_service.CONFIG.search_log_max_new_queries_per_ip_per_day",
            2,
        )

        for q in ("primeira", "segunda", "terceira", "quarta", "segunda"):
            _log(public_client, q)

        assert {(log.query, log.searches) for log in _logs(session)} == {
            ("primeira", 1),
            ("segunda", 2),
        }

    def test_flood_of_one_query_is_a_single_row(
        self, public_client: TestClient, session: Session, fake_redis: FakeAsyncRedis
    ) -> None:
        for _ in range(30):
            _log(public_client, "flood")

        [log] = _logs(session)
        assert log.searches == 30
